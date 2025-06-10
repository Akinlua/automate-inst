#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

# Fix Windows Unicode encoding issues
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    # Set console codepage to UTF-8 if possible
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    except:
        pass

#!/usr/bin/env python3
"""
Instagram Auto Poster Web Interface
Beautiful Flask web application for managing Instagram posting
"""

import os
import csv
import json
import shutil
import logging
import time as time_module
from datetime import datetime, timedelta, date, time as datetime_time
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
from instagram_poster import InstagramPoster
from setup_integration import web_setup
import pytz
from dotenv import load_dotenv
import ssl
import urllib3
import threading
import signal
import atexit
from PIL import Image
import base64
import time
# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


# VNC Support
try:
    from vnc_setup import start_vnc_chrome_session, get_vnc_status, get_vnc_access_info, stop_vnc_session
    VNC_AVAILABLE = True
except ImportError as e:
    logger.warning(f"VNC support not available: {e}")
    VNC_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Configuration
UPLOAD_FOLDER = Path('content')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_CSV_EXTENSIONS = {'csv'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_month_stats(month_num):
    """Get statistics for a specific month"""
    month_folder = UPLOAD_FOLDER / str(month_num)
    
    stats = {
        'month': month_num,
        'images': 0,
        'captions': 0,
        'posts_available': 0,
        'posts_used': 0,
        'images_used': 0,
        'last_post': None
    }
    
    if not month_folder.exists():
        return stats
    
    # Count images
    image_files = [f for f in month_folder.iterdir() 
                   if f.is_file() and f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp', '.gif'}]
    stats['images'] = len(image_files)
    
    # Count captions from CSV
    csv_file = None
    for file in month_folder.iterdir():
        if file.is_file() and file.suffix.lower() == '.csv':
            csv_file = file
            break
    
    if csv_file:
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                captions = []
                for row in reader:
                    if row and len(row) >= 2 and row[1].strip():
                        captions.append(row[1].strip())
                stats['captions'] = len(captions)
        except:
            stats['captions'] = 0
    
    # Get usage stats from posted content
    poster = InstagramPoster()
    month_key = f"month_{month_num}"
    posted_data = poster.posted_content.get(month_key, {})
    
    stats['posts_used'] = len(posted_data.get('used_posts', []))
    stats['images_used'] = len(posted_data.get('used_images', []))
    stats['posts_available'] = stats['captions'] - stats['posts_used']
    
    # Last post info
    post_history = posted_data.get('post_history', [])
    if post_history:
        last_post = post_history[-1]
        stats['last_post'] = datetime.fromisoformat(last_post['posted_at']).strftime('%Y-%m-%d %H:%M')
    
    return stats

@app.route('/')
def index():
    """Main dashboard"""
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    months_data = []
    for i in range(1, 13):
        stats = get_month_stats(i)
        stats['name'] = month_names[i-1]
        months_data.append(stats)
    
    current_month = datetime.now().month
    
    # Get scheduler errors
    poster = InstagramPoster()
    scheduler_errors = poster.get_scheduler_errors()
    
    return render_template('index.html', 
                         months=months_data, 
                         current_month=current_month,
                         scheduler_errors=scheduler_errors)

@app.route('/month/<int:month_num>')
def month_detail(month_num):
    """Month detail page"""
    if month_num < 1 or month_num > 12:
        flash('Invalid month number', 'error')
        return redirect(url_for('index'))
    
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    month_folder = UPLOAD_FOLDER / str(month_num)
    month_folder.mkdir(exist_ok=True)
    
    # Get posted content info
    poster = InstagramPoster()
    month_key = f"month_{month_num}"
    posted_data = poster.posted_content.get(month_key, {})
    used_images = set(posted_data.get('used_images', []))
    used_posts = set(posted_data.get('used_posts', []))
    
    # Get images using the new ordering system
    ordered_image_names = poster.get_month_image_order(month_num)
    images = []
    for image_name in ordered_image_names:
        image_info = {
            'name': image_name,
            'is_used': image_name in used_images
        }
        images.append(image_info)
    
    # Get captions from CSV
    captions = []
    csv_file = None
    for file in month_folder.iterdir():
        if file.is_file() and file.suffix.lower() == '.csv':
            csv_file = file
            break
    
    if csv_file:
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and len(row) >= 2 and row[1].strip():
                        caption_info = {
                            'id': row[0], 
                            'text': row[1].strip(),
                            'index': len(captions),  # For display order
                            'is_used': row[0] in used_posts
                        }
                        captions.append(caption_info)
        except Exception as e:
            flash(f'Error reading CSV file: {e}', 'error')
    
    stats = get_month_stats(month_num)
    
    # Get scheduler errors for this month
    scheduler_errors = [
        error for error in poster.get_scheduler_errors() 
        if error.get('month') == month_num
    ]
    
    return render_template('month_detail.html', 
                         month_num=month_num,
                         month_name=month_names[month_num-1],
                         images=images,
                         captions=captions,
                         stats=stats,
                         scheduler_errors=scheduler_errors)

@app.route('/upload_images/<int:month_num>', methods=['POST'])
def upload_images(month_num):
    """Upload images for a specific month"""
    if 'files' not in request.files:
        flash('No files selected', 'error')
        return redirect(url_for('month_detail', month_num=month_num))
    
    files = request.files.getlist('files')
    month_folder = UPLOAD_FOLDER / str(month_num)
    month_folder.mkdir(exist_ok=True)
    
    uploaded_count = 0
    for file in files:
        if file and file.filename and allowed_file(file.filename, ALLOWED_EXTENSIONS):
            # Get timestamp for unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Remove last 3 digits of microseconds
            
            # Get file extension
            original_filename = secure_filename(file.filename)
            name, ext = os.path.splitext(original_filename)
            
            # Create new filename with timestamp
            filename = f"{timestamp}_{name}{ext}"
            
            file_path = month_folder / filename
            file.save(file_path)
            uploaded_count += 1
    
    flash(f'Successfully uploaded {uploaded_count} images', 'success')
    return redirect(url_for('month_detail', month_num=month_num))

@app.route('/upload_csv/<int:month_num>', methods=['POST'])
def upload_csv(month_num):
    """Upload or update CSV file for a specific month"""
    if 'csv_file' not in request.files:
        flash('No CSV file selected', 'error')
        return redirect(url_for('month_detail', month_num=month_num))
    
    file = request.files['csv_file']
    if not file or not file.filename or not allowed_file(file.filename, ALLOWED_CSV_EXTENSIONS):
        flash('Invalid CSV file', 'error')
        return redirect(url_for('month_detail', month_num=month_num))
    
    month_folder = UPLOAD_FOLDER / str(month_num)
    month_folder.mkdir(exist_ok=True)
    
    # Find existing CSV file
    existing_csv = None
    for existing_file in month_folder.iterdir():
        if existing_file.is_file() and existing_file.suffix.lower() == '.csv':
            existing_csv = existing_file
            break
    
    try:
        # Read new CSV content
        new_captions = []
        file.stream.seek(0)
        content = file.stream.read().decode('utf-8')
        reader = csv.reader(content.splitlines())
        for row in reader:
            if row and len(row) >= 1 and row[0].strip():
                # Handle both old format (caption only) and new format (id,caption)
                if len(row) >= 2:
                    # New format: id,caption
                    new_captions.append(row[1].strip())
                else:
                    # Old format: caption only
                    new_captions.append(row[0].strip())
        
        # Read existing CSV content if exists
        existing_captions = []
        next_id = 1
        if existing_csv:
            with open(existing_csv, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and len(row) >= 2 and row[1].strip():
                        existing_captions.append(row[1].strip())
                        try:
                            next_id = max(next_id, int(row[0]) + 1)
                        except:
                            next_id = len(existing_captions) + 1
        
        # Add new captions that don't already exist
        captions_to_add = [cap for cap in new_captions if cap not in existing_captions]
        
        # Write to CSV file with ID,caption format
        csv_filename = existing_csv.name if existing_csv else 'captions.csv'
        csv_path = month_folder / csv_filename
        
        # Read existing data first
        all_captions = []
        if existing_csv:
            with open(existing_csv, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row and len(row) >= 2 and row[1].strip():
                        all_captions.append([row[0], row[1]])
        
        # Add new captions with sequential IDs
        for caption in captions_to_add:
            all_captions.append([str(next_id), caption])
            next_id += 1
        
        # Write back to file
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for caption_data in all_captions:
                writer.writerow(caption_data)
        
        flash(f'Successfully added {len(captions_to_add)} new captions', 'success')
        
    except Exception as e:
        flash(f'Error processing CSV file: {e}', 'error')
    
    return redirect(url_for('month_detail', month_num=month_num))

@app.route('/post_now', methods=['POST'])
def post_now():
    """Post content immediately"""
    try:
        num_images = int(request.form.get('num_images', 1))
        
        poster = InstagramPoster()
        
        # Get content for current month
        try:
            content = poster.get_current_month_content_new(num_images)
        except ValueError as e:
            # Handle insufficient images error
            return jsonify({'success': False, 'message': str(e)})
        
        if not content:
            return jsonify({'success': False, 'message': 'No content available for current month'})
        
        folder, images, caption, post_number = content
        current_month = int(folder.name)
        
        # Enhance text with ChatGPT if enabled
        enhanced_text = poster.enhance_text_with_chatgpt(caption)
        
        # Add month info to caption
        month_names = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        month_name = month_names[current_month - 1]
        
        final_caption = f"{enhanced_text}"
        
        # Setup driver and post
        if not poster.setup_chrome_driver():
            return jsonify({'success': False, 'message': 'Failed to setup Chrome driver'})
        
        try:
            if not poster.navigate_to_instagram():
                return jsonify({'success': False, 'message': 'Failed to navigate to Instagram'})
            
            # Post to Instagram (using all selected images)
            if poster.post_to_instagram(images, final_caption):
                poster.mark_content_as_posted(current_month, post_number, [img.name for img in images])
                return jsonify({'success': True, 'message': f'Successfully posted content #{post_number} with {len(images)} images'})
            else:
                return jsonify({'success': False, 'message': 'Failed to post to Instagram'})
                
        finally:
            if poster.driver:
                poster.driver.quit()
                
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@app.route('/api/stats')
def api_stats():
    """API endpoint for getting stats"""
    month_num = request.args.get('month', type=int)
    if month_num:
        return jsonify(get_month_stats(month_num))
    
    # Return all months stats
    all_stats = []
    for i in range(1, 13):
        all_stats.append(get_month_stats(i))
    
    return jsonify(all_stats)

@app.route('/api/scheduler/settings', methods=['GET'])
def get_scheduler_settings():
    """Get scheduler settings"""
    try:
        poster = InstagramPoster()
        return jsonify({
            'success': True,
            'settings': poster.settings
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting settings: {str(e)}'
        })

@app.route('/api/scheduler/settings', methods=['POST'])
def update_scheduler_settings():
    """Update scheduler settings"""
    try:
        data = request.get_json()
        poster = InstagramPoster()
        
        # Update specific settings
        if 'num_images' in data:
            num_images = int(data['num_images'])
            if 1 <= num_images <= 10:
                poster.update_setting('num_images', num_images)
            else:
                return jsonify({
                    'success': False,
                    'message': 'Number of images must be between 1 and 10'
                })
        
        if 'post_interval_hours' in data:
            interval = int(data['post_interval_hours'])
            if 1 <= interval <= 24:
                poster.update_setting('post_interval_hours', interval)
            else:
                return jsonify({
                    'success': False,
                    'message': 'Post interval must be between 1 and 24 hours'
                })
        
        if 'enabled' in data:
            poster.update_setting('enabled', bool(data['enabled']))
        
        return jsonify({
            'success': True,
            'message': 'Settings updated successfully',
            'settings': poster.settings
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error updating settings: {str(e)}'
        })

@app.route('/api/scheduler/start', methods=['POST'])
def start_scheduler():
    """Start the scheduler"""
    try:
        global scheduler_manager
        if scheduler_manager is None:
            scheduler_manager = SchedulerManager()
        
        if scheduler_manager.start_scheduler():
            return jsonify({
                'success': True,
                'message': 'Scheduler started successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Scheduler is already running'
            })
    except Exception as e:
        logger.error(f"Error starting scheduler: {e}")
        return jsonify({
            'success': False,
            'message': f'Error starting scheduler: {str(e)}'
        })

@app.route('/api/scheduler/stop', methods=['POST'])
def stop_scheduler():
    """Stop the scheduler"""
    try:
        global scheduler_manager
        if scheduler_manager is None:
            return jsonify({
                'success': False,
                'message': 'Scheduler is not running'
            })
        
        if scheduler_manager.stop_scheduler():
            return jsonify({
                'success': True,
                'message': 'Scheduler stopped successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Scheduler was not running'
            })
    except Exception as e:
        logger.error(f"Error stopping scheduler: {e}")
        return jsonify({
            'success': False,
            'message': f'Error stopping scheduler: {str(e)}'
        })

@app.route('/api/scheduler/status')
def get_scheduler_status():
    try:
        global scheduler_manager
        
        # Check if scheduler is enabled
        settings_file = os.path.join('scheduler_settings.json')
        scheduler_enabled = False
        posting_times = []
        num_images = 1
        timezone = 'UTC'
        
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as f:
                settings = json.load(f)
                scheduler_enabled = settings.get('enabled', False)
                posting_times = settings.get('posting_times', [])
                num_images = settings.get('num_images', 1)
                timezone = settings.get('timezone', 'UTC')
        
        # Get recent errors
        errors_file = os.path.join('scheduler_errors.json')
        recent_errors = []
        if os.path.exists(errors_file):
            with open(errors_file, 'r') as f:
                all_errors = json.load(f)
                recent_errors = all_errors[-5:] if all_errors else []
        
        # Get last successful post time
        last_post_time = None
        posted_file = os.path.join('posted_content.json')
        if os.path.exists(posted_file):
            with open(posted_file, 'r') as f:
                posted_data = json.load(f)
                if posted_data:
                    # Get the most recent post
                    latest_timestamp = None
                    for month_data in posted_data.values():
                        if 'post_history' in month_data:
                            for post in month_data['post_history']:
                                if latest_timestamp is None or post.get('posted_at', '') > latest_timestamp:
                                    latest_timestamp = post.get('posted_at')
                    last_post_time = latest_timestamp
        
        # Get scheduler manager status
        scheduler_running = False
        if scheduler_manager is not None:
            manager_status = scheduler_manager.get_status()
            scheduler_running = manager_status['running']
        
        status = {
            'enabled': scheduler_enabled,
            'running': scheduler_running,
            'posting_times': posting_times,
            'num_images': num_images,
            'timezone': timezone,
            'recent_errors': recent_errors,
            'last_post_time': last_post_time,
            'next_post_time': None
        }
        
        # Calculate next post time with timezone support
        if scheduler_enabled and scheduler_running and posting_times:
            try:
                user_tz = pytz.timezone(timezone)
                # Automatically detect server timezone using system's local time
                try:
                    # Use Python's built-in timezone detection (Python 3.6+)
                    import datetime as dt
                    system_tz = dt.datetime.now().astimezone().tzinfo
                    # Convert to pytz timezone for compatibility
                    server_tz_str = str(system_tz)
                    
                    # Try to create pytz timezone from the detected timezone
                    if hasattr(system_tz, 'zone'):
                        # It's already a pytz timezone
                        server_tz = system_tz
                    else:
                        # Try to match with pytz timezones
                        try:
                            # First try: Extract timezone name from tzfile format
                            import re
                            tz_match = re.search(r'tzfile\(\'([^\']+)\'\)', server_tz_str)
                            if tz_match:
                                server_tz = pytz.timezone(tz_match.group(1))
                            else:
                                # Second try: Handle simple timezone abbreviations like WAT, EST, etc.
                                if server_tz_str in ['WAT']:
                                    # WAT is UTC+1 (West Africa Time)
                                    server_tz = pytz.timezone('Africa/Lagos')  # WAT timezone
                                elif server_tz_str in ['PST']:
                                    server_tz = pytz.timezone('US/Pacific')
                                elif server_tz_str in ['EST']:
                                    server_tz = pytz.timezone('US/Eastern')
                                elif server_tz_str in ['UTC']:
                                    server_tz = pytz.timezone('UTC')
                                else:
                                    # Third try: use UTC offset to find appropriate timezone
                                    offset = dt.datetime.now().astimezone().utcoffset()
                                    hours_offset = offset.total_seconds() / 3600
                                    
                                    # Map common offsets to timezones
                                    offset_to_tz = {
                                        0: 'UTC',
                                        1: 'Europe/Berlin',  # CET
                                        -5: 'US/Eastern',    # EST
                                        -8: 'US/Pacific',    # PST
                                        8: 'Asia/Shanghai',  # CST
                                        9: 'Asia/Tokyo',     # JST
                                    }
                                    
                                    if hours_offset in offset_to_tz:
                                        server_tz = pytz.timezone(offset_to_tz[hours_offset])
                                    else:
                                        # Fallback: use UTC
                                        server_tz = pytz.timezone('UTC')
                        except:
                            server_tz = pytz.timezone('UTC')
                except:
                    # Final fallback to UTC
                    server_tz = pytz.timezone('UTC')
                
                # Get current time in both timezones
                now_utc = datetime.now(server_tz)
                now_user = now_utc.astimezone(user_tz)
                today = now_user.date()
                
                # Convert all posting times to server time and find the next one
                upcoming_times = []
                
                for time_str in posting_times:
                    hour, minute = map(int, time_str.split(':'))
                    
                    # Check today's posting time
                    target_datetime = datetime.combine(today, datetime_time(hour=hour, minute=minute))
                    user_time = user_tz.localize(target_datetime)
                    server_time = user_time.astimezone(server_tz)
                    
                    # If this time hasn't passed today, add it
                    if server_time > now_utc:
                        upcoming_times.append(server_time)
                    else:
                        # Add tomorrow's time
                        tomorrow = today + timedelta(days=1)
                        target_datetime = datetime.combine(tomorrow, datetime_time(hour=hour, minute=minute))
                        user_time = user_tz.localize(target_datetime)
                        server_time = user_time.astimezone(server_tz)
                        upcoming_times.append(server_time)
                
                if upcoming_times:
                    next_time = min(upcoming_times)
                    # Convert back to user timezone for display
                    next_time_user = next_time.astimezone(user_tz)
                    status['next_post_time'] = next_time_user.strftime('%Y-%m-%d %H:%M:%S %Z')
                    
            except Exception as e:
                # Fallback to original logic if timezone handling fails
                logger.error(f"Timezone conversion error: {e}")
                status['next_post_time'] = None
        
        return jsonify(status)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/settings')
def settings():
    """Settings page"""
    return render_template('settings.html')

@app.route('/images/<int:month_num>/<filename>')
def serve_image(month_num, filename):
    """Serve images from the content directory"""
    try:
        month_folder = UPLOAD_FOLDER / str(month_num)
        return send_from_directory(month_folder, filename)
    except Exception as e:
        # Return a placeholder image or 404
        return f"Image not found: {filename}", 404

@app.route('/create_sample_content', methods=['POST'])
def create_sample_content():
    """Create sample CSV files for all months"""
    try:
        content_dir = Path('content')
        content_dir.mkdir(exist_ok=True)
        
        created_months = []
        
        # Create folders for months 1-12
        for month in range(1, 13):
            month_dir = content_dir / str(month)
            month_dir.mkdir(exist_ok=True)
            
            # Create sample CSV file with captions (only if it doesn't exist)
            csv_file = month_dir / 'captions.csv'
            if not csv_file.exists():
                with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['1', f"First amazing post for month {month}! 🌟 #month{month} #content"])
                    writer.writerow(['2', f"Second incredible post for month {month}! ✨ #instagram #amazing"])
                    writer.writerow(['3', f"Third fantastic post for month {month}! 🚀 #social #media"])
                    writer.writerow(['4', f"Fourth wonderful post for month {month}! 💫 #creative #content"])
                    writer.writerow(['5', f"Fifth awesome post for month {month}! 🎯 #engagement #growth"])
                
                created_months.append(month)
        
        if created_months:
            flash(f'Successfully created sample content for {len(created_months)} months', 'success')
        else:
            flash('Sample content already exists for all months', 'info')
        
        return jsonify({'success': True, 'message': f'Sample content created for {len(created_months)} months'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error creating sample content: {str(e)}'})

@app.route('/delete_caption/<int:month_num>', methods=['POST'])
def delete_caption(month_num):
    """Delete a specific caption"""
    try:
        data = request.get_json()
        caption_id = data.get('id')
        
        if not caption_id:
            return jsonify({'success': False, 'message': 'Caption ID is required'})
        
        month_folder = UPLOAD_FOLDER / str(month_num)
        csv_file = None
        for file in month_folder.iterdir():
            if file.is_file() and file.suffix.lower() == '.csv':
                csv_file = file
                break
        
        if not csv_file:
            return jsonify({'success': False, 'message': 'No CSV file found'})
        
        # Read all captions
        captions = []
        found = False
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row and len(row) >= 2:
                    if row[0] == caption_id:
                        found = True
                        continue  # Skip this caption (delete it)
                    captions.append([row[0], row[1]])
        
        if not found:
            return jsonify({'success': False, 'message': 'Caption not found'})
        
        # Write back to file
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for caption_data in captions:
                writer.writerow(caption_data)
        
        # Clean up from posted content
        poster = InstagramPoster()
        month_key = f"month_{month_num}"
        posted_data = poster.posted_content.get(month_key, {})
        used_posts = posted_data.get('used_posts', [])
        
        if caption_id in used_posts:
            used_posts.remove(caption_id)
            poster.posted_content[month_key]['used_posts'] = used_posts
            poster.save_posted_content()
        
        return jsonify({'success': True, 'message': 'Caption deleted successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error deleting caption: {str(e)}'})

@app.route('/delete_all_captions/<int:month_num>', methods=['POST'])
def delete_all_captions(month_num):
    """Delete all captions for a specific month"""
    try:
        month_folder = UPLOAD_FOLDER / str(month_num)
        csv_file = None
        for file in month_folder.iterdir():
            if file.is_file() and file.suffix.lower() == '.csv':
                csv_file = file
                break
        
        if not csv_file:
            return jsonify({'success': False, 'message': 'No CSV file found'})
        
        # Count captions before deletion
        caption_count = 0
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row and len(row) >= 2:
                    caption_count += 1
        
        # Delete the CSV file
        csv_file.unlink()
        
        # Clean up from posted content
        poster = InstagramPoster()
        month_key = f"month_{month_num}"
        if month_key in poster.posted_content:
            poster.posted_content[month_key]['used_posts'] = []
            poster.save_posted_content()
        
        return jsonify({'success': True, 'message': f'Successfully deleted {caption_count} captions'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error deleting all captions: {str(e)}'})

@app.route('/delete_all_images/<int:month_num>', methods=['POST'])
def delete_all_images(month_num):
    """Delete all images for a specific month"""
    try:
        month_folder = UPLOAD_FOLDER / str(month_num)
        
        if not month_folder.exists():
            return jsonify({'success': False, 'message': 'Month folder not found'})
        
        # Get all image files
        image_files = [f for f in month_folder.iterdir() 
                      if f.is_file() and f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp', '.gif'}]
        
        if not image_files:
            return jsonify({'success': False, 'message': 'No images found'})
        
        # Delete all images
        deleted_count = 0
        for image_file in image_files:
            try:
                image_file.unlink()
                deleted_count += 1
            except Exception as e:
                print(f"Error deleting {image_file}: {e}")
        
        # Clean up from posted content and image order
        poster = InstagramPoster()
        month_key = f"month_{month_num}"
        
        # Clear used images from posted content
        if month_key in poster.posted_content:
            poster.posted_content[month_key]['used_images'] = []
            poster.save_posted_content()
        
        # Clear image order
        poster.clear_month_image_order(month_num)
        
        return jsonify({'success': True, 'message': f'Successfully deleted {deleted_count} images'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error deleting all images: {str(e)}'})

@app.route('/delete_image/<int:month_num>/<filename>', methods=['POST'])
def delete_image(month_num, filename):
    """Delete a specific image from a month folder"""
    try:
        month_folder = UPLOAD_FOLDER / str(month_num)
        image_path = month_folder / secure_filename(filename)
        
        if image_path.exists() and image_path.is_file():
            image_path.unlink()
            
            # Clean up from posted content
            poster = InstagramPoster()
            month_key = f"month_{month_num}"
            posted_data = poster.posted_content.get(month_key, {})
            used_images = posted_data.get('used_images', [])
            
            if filename in used_images:
                used_images.remove(filename)
                poster.posted_content[month_key]['used_images'] = used_images
                poster.save_posted_content()
            
            # Remove from image order
            poster.remove_from_month_image_order(month_num, filename)
            
            flash(f'Successfully deleted {filename}', 'success')
            return jsonify({'success': True, 'message': f'Successfully deleted {filename}'})
        else:
            return jsonify({'success': False, 'message': 'Image not found'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error deleting image: {str(e)}'})

@app.route('/edit_caption/<int:month_num>', methods=['POST'])
def edit_caption(month_num):
    """Edit a specific caption"""
    try:
        data = request.get_json()
        caption_id = data.get('id')
        new_text = data.get('text', '').strip()
        
        if not caption_id or not new_text:
            return jsonify({'success': False, 'message': 'Missing caption ID or text'})
        
        month_folder = UPLOAD_FOLDER / str(month_num)
        csv_file = None
        for file in month_folder.iterdir():
            if file.is_file() and file.suffix.lower() == '.csv':
                csv_file = file
                break
        
        if not csv_file:
            return jsonify({'success': False, 'message': 'No CSV file found'})
        
        # Read all captions
        captions = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row and len(row) >= 2:
                    captions.append([row[0], row[1]])
        
        # Update the specific caption
        updated = False
        for i, caption in enumerate(captions):
            if caption[0] == caption_id:
                captions[i][1] = new_text
                updated = True
                break
        
        if not updated:
            return jsonify({'success': False, 'message': 'Caption not found'})
        
        # Write back to file
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for caption_data in captions:
                writer.writerow(caption_data)
        
        return jsonify({'success': True, 'message': 'Caption updated successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error updating caption: {str(e)}'})

@app.route('/add_caption/<int:month_num>', methods=['POST'])
def add_caption(month_num):
    """Add new caption(s) to CSV file"""
    try:
        data = request.get_json()
        input_text = data.get('text', '').strip()
        
        if not input_text:
            return jsonify({'success': False, 'message': 'Caption text is required'})
        
        month_folder = UPLOAD_FOLDER / str(month_num)
        month_folder.mkdir(exist_ok=True)
        
        # Find or create CSV file
        csv_file = None
        for file in month_folder.iterdir():
            if file.is_file() and file.suffix.lower() == '.csv':
                csv_file = file
                break
        
        if not csv_file:
            csv_file = month_folder / 'captions.csv'
        
        # Read existing captions to check for duplicates and get next ID
        existing_captions = {}
        max_id_num = 0
        
        if csv_file.exists():
            try:
                with open(csv_file, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if row and len(row) >= 2:
                            existing_captions[row[0]] = row[1]
                            # Try to extract number from ID for auto-increment
                            try:
                                if row[0].startswith('post'):
                                    num = int(row[0][4:])  # Extract number after 'post'
                                    max_id_num = max(max_id_num, num)
                            except:
                                pass
            except Exception as e:
                return jsonify({'success': False, 'message': f'Error reading existing captions: {str(e)}'})
        
        # Parse input lines
        lines = input_text.split('\n')
        new_captions = []
        errors = []
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
                
            # Check if line contains comma (id,caption format)
            if ',' in line:
                parts = line.split(',', 1)  # Split only on first comma
                caption_id = parts[0].strip()
                caption_text = parts[1].strip()
                
                if not caption_id or not caption_text:
                    errors.append(f"Line {line_num}: Both ID and caption text are required")
                    continue
                    
                if caption_id in existing_captions:
                    errors.append(f"Line {line_num}: ID '{caption_id}' already exists")
                    continue
                    
                # Check for duplicates within this input
                if any(cap[0] == caption_id for cap in new_captions):
                    errors.append(f"Line {line_num}: Duplicate ID '{caption_id}' in input")
                    continue
                    
                new_captions.append((caption_id, caption_text))
            else:
                # Caption only format - auto-assign ID
                caption_text = line.strip()
                if not caption_text:
                    continue
                    
                # Generate next available ID
                max_id_num += 1
                caption_id = f"post{max_id_num}"
                
                # Ensure this auto-generated ID doesn't exist
                while caption_id in existing_captions or any(cap[0] == caption_id for cap in new_captions):
                    max_id_num += 1
                    caption_id = f"post{max_id_num}"
                
                new_captions.append((caption_id, caption_text))
        
        if not new_captions and not errors:
            return jsonify({'success': False, 'message': 'No valid captions found in input'})
        
        if new_captions:
            # Append new captions to CSV file
            try:
                with open(csv_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    for caption_id, caption_text in new_captions:
                        writer.writerow([caption_id, caption_text])
                        
                success_msg = f"Successfully added {len(new_captions)} caption(s)"
                if errors:
                    success_msg += f". {len(errors)} error(s) occurred: " + "; ".join(errors)
                    
                return jsonify({'success': True, 'message': success_msg})
                
            except Exception as e:
                return jsonify({'success': False, 'message': f'Error writing to CSV file: {str(e)}'})
        else:
            error_msg = f"No captions added. Errors: " + "; ".join(errors)
            return jsonify({'success': False, 'message': error_msg})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error adding caption(s): {str(e)}'})

@app.route('/reorder_captions/<int:month_num>', methods=['POST'])
def reorder_captions(month_num):
    """Reorder captions based on new order"""
    try:
        data = request.get_json()
        new_order = data.get('order', [])  # List of caption IDs in new order
        
        if not new_order:
            return jsonify({'success': False, 'message': 'New order is required'})
        
        month_folder = UPLOAD_FOLDER / str(month_num)
        csv_file = None
        for file in month_folder.iterdir():
            if file.is_file() and file.suffix.lower() == '.csv':
                csv_file = file
                break
        
        if not csv_file:
            return jsonify({'success': False, 'message': 'No CSV file found'})
        
        # Read all captions into a dictionary
        captions_dict = {}
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row and len(row) >= 2:
                    captions_dict[row[0]] = row[1]
        
        # Reorder captions based on new order
        reordered_captions = []
        for caption_id in new_order:
            if caption_id in captions_dict:
                reordered_captions.append([caption_id, captions_dict[caption_id]])
        
        # Write back to file
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for caption_data in reordered_captions:
                writer.writerow(caption_data)
        
        return jsonify({'success': True, 'message': 'Captions reordered successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error reordering captions: {str(e)}'})

@app.route('/reorder_images/<int:month_num>', methods=['POST'])
def reorder_images(month_num):
    """Reorder images based on new order using JSON storage instead of renaming files"""
    try:
        data = request.get_json()
        new_order = data.get('order', [])  # List of filenames in new order
        
        if not new_order:
            return jsonify({'success': False, 'message': 'New order is required'})
        
        poster = InstagramPoster()
        
        # Update the image order using the new system
        if poster.update_month_image_order(month_num, new_order):
            return jsonify({'success': True, 'message': 'Images reordered successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to update image order'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error reordering images: {str(e)}'})

@app.route('/clear_scheduler_errors', methods=['POST'])
def clear_scheduler_errors():
    """Clear scheduler errors"""
    try:
        poster = InstagramPoster()
        poster.clear_scheduler_errors()
        return jsonify({'success': True, 'message': 'Scheduler errors cleared successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error clearing scheduler errors: {str(e)}'})

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get current settings"""
    try:
        poster = InstagramPoster()
        settings = poster.settings
        return jsonify(settings)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/settings', methods=['POST'])
def save_settings():
    """Save settings"""
    try:
        data = request.get_json()
        poster = InstagramPoster()
        
        # Update settings
        if 'enabled' in data:
            poster.update_setting('enabled', data['enabled'])
        if 'num_images' in data:
            poster.update_setting('num_images', data['num_images'])
        if 'posting_times' in data:
            poster.update_setting('posting_times', data['posting_times'])
        if 'timezone' in data:
            poster.update_setting('timezone', data['timezone'])
        if 'chatgpt_enabled' in data:
            poster.update_setting('chatgpt_enabled', data['chatgpt_enabled'])
        if 'chatgpt_api_key' in data:
            poster.update_setting('chatgpt_api_key', data['chatgpt_api_key'])
        
        return jsonify({'success': True, 'message': 'Settings saved successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/settings/reload', methods=['POST'])
def reload_settings():
    """Reload settings from file"""
    try:
        poster = InstagramPoster()
        poster.load_settings()
        return jsonify({'success': True, 'message': 'Settings reloaded successfully'})
    except Exception as e:
        logger.error(f"Error reloading settings: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# Instagram Login Setup API Endpoints
@app.route('/api/login/start', methods=['POST'])
def start_instagram_login():
    """Start Instagram login setup process"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({'success': False, 'error': 'Username and password are required'}), 400
        
        result = web_setup.start_setup(username, password)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error starting login setup: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/login/status')
def get_login_status():
    """Get current login setup status"""
    try:
        status = web_setup.get_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting login status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/login/verify', methods=['POST'])
def submit_verification_code():
    """Submit email verification code"""
    try:
        data = request.get_json()
        code = data.get('code', '').strip()
        
        if not code:
            return jsonify({'success': False, 'error': 'Verification code is required'}), 400
        
        result = web_setup.submit_verification_code(code)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error submitting verification code: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/login/logout', methods=['POST'])
def logout_instagram():
    """Logout from Instagram (delete Chrome profile)"""
    try:
        result = web_setup.logout()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error during logout: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/login/check')
def check_login_status():
    """Check if user is currently logged in"""
    try:
        is_logged_in = web_setup.is_logged_in()
        # Load environment variables
        load_dotenv()
        
        profile_path = os.getenv('CHROME_PROFILE_PATH')
        print(f"Profile path: {profile_path}")
        
        return jsonify({
            'logged_in': is_logged_in,
            'chrome_profile_path': profile_path if is_logged_in else None
        })
    except Exception as e:
        logger.error(f"Error checking login status: {e}")
        return jsonify({'error': str(e)}), 500

# VNC Manual Login API Endpoints
@app.route('/api/vnc/start', methods=['POST'])
def start_vnc_session():
    """Start VNC session for manual Instagram login"""
    try:
        if not VNC_AVAILABLE:
            return jsonify({
                'success': False, 
                'error': 'VNC support is not available on this system'
            }), 500
            
        # Get or create profile path
        profile_path = os.getenv('CHROME_PROFILE_PATH')
        if not profile_path:
            profile_path = os.path.join(os.getcwd(), "chrome_profile_instagram")
            
        logger.info(f"Starting VNC session with profile: {profile_path}")
        
        # Run async function using asyncio.run()
        import asyncio
        result = asyncio.run(start_vnc_chrome_session(profile_path))
        
        if result['success']:
            logger.info("VNC session started successfully")
            return jsonify(result)
        else:
            logger.error(f"VNC session failed: {result.get('error')}")
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Error starting VNC session: {e}")
        return jsonify({
            'success': False, 
            'error': f'Failed to start VNC session: {str(e)}'
        }), 500

@app.route('/api/vnc/status')
def get_vnc_session_status():
    """Get current VNC session status"""
    try:
        if not VNC_AVAILABLE:
            return jsonify({
                'vnc_available': False,
                'error': 'VNC support not available'
            })
            
        # Run async function using asyncio.run()
        import asyncio
        status = asyncio.run(get_vnc_status())
        access_info = get_vnc_access_info()
        
        return jsonify({
            'vnc_available': True,
            'status': status,
            'access_info': access_info
        })
        
    except Exception as e:
        logger.error(f"Error getting VNC status: {e}")
        return jsonify({
            'vnc_available': False,
            'error': str(e)
        }), 500

@app.route('/api/vnc/stop', methods=['POST'])
def stop_vnc_session_endpoint():
    """Stop VNC session"""
    try:
        if not VNC_AVAILABLE:
            return jsonify({
                'success': False,
                'error': 'VNC support not available'
            }), 500
            
        # Run async function using asyncio.run()
        import asyncio
        asyncio.run(stop_vnc_session())
        
        return jsonify({
            'success': True,
            'message': 'VNC session stopped successfully'
        })
        
    except Exception as e:
        logger.error(f"Error stopping VNC session: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/vnc/check')
def check_vnc_availability():
    """Check if VNC is available and system compatibility"""
    try:
        return jsonify({
            'vnc_available': VNC_AVAILABLE,
            'system_info': {
                'platform': os.name,
                'python_version': f"{os.sys.version_info.major}.{os.sys.version_info.minor}",
                'current_user': os.getenv('USER', 'unknown')
            }
        })
    except Exception as e:
        logger.error(f"Error checking VNC availability: {e}")
        return jsonify({
            'vnc_available': False,
            'error': str(e)
        }), 500

@app.route('/api/setup/chrome_local', methods=['POST'])
def start_local_chrome_setup():
    """Start local Chrome setup using setup_chromev1.py"""
    try:
        import subprocess
        import threading
        
        def run_chrome_setup():
            """Run Chrome setup in background thread"""
            try:
                # Run setup_chromev1.py
                result = subprocess.run([
                    'python3', 'setup_chromev1.py'
                ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
                
                logger.info(f"Chrome setup completed with return code: {result.returncode}")
                if result.stdout:
                    logger.info(f"Chrome setup output: {result.stdout}")
                if result.stderr:
                    logger.warning(f"Chrome setup errors: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                logger.warning("Chrome setup timed out after 5 minutes")
            except Exception as e:
                logger.error(f"Error running Chrome setup: {e}")
        
        # Start Chrome setup in background
        setup_thread = threading.Thread(target=run_chrome_setup, daemon=True)
        setup_thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Local Chrome setup started. Check your screen for the Chrome window.'
        })
        
    except Exception as e:
        logger.error(f"Error starting local Chrome setup: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/login/chrome_setup', methods=['POST'])
def start_chrome_login_setup():
    """Start Chrome login setup integrated into the web interface"""
    try:
        import subprocess
        import threading
        import os
        import time
        import undetected_chromedriver as uc
        from selenium.webdriver.chrome.options import Options
        
        # Clean up any existing flag files
        flag_files = ['chrome_login_complete.flag', 'chrome_login_error.flag']
        for flag_file in flag_files:
            if os.path.exists(flag_file):
                os.remove(flag_file)
        
        def run_integrated_chrome_setup():
            """Run Chrome setup integrated with Instagram navigation"""
            try:
                logger.info("Starting integrated Chrome login setup")
                
                # Disable SSL warnings and create unverified SSL context (from setup_chromev1.py)
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                ssl._create_default_https_context = ssl._create_unverified_context
                
                # Use the same profile path as setup_chromev1.py
                CUSTOM_PROFILE_PATH = os.path.join(os.getcwd(), "chrome_profile_instagram")
                
                # Create fresh profile directory if it doesn't exist
                os.makedirs(CUSTOM_PROFILE_PATH, exist_ok=True)
                logger.info(f"Using Chrome profile: {CUSTOM_PROFILE_PATH}")
                
                # Setup Chrome options (similar to setup_chromev1.py)
                options = uc.ChromeOptions()
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-blink-features=AutomationControlled')

                options.add_argument(f"--user-data-dir={CUSTOM_PROFILE_PATH}")
                options.add_argument("--profile-directory=Default")
                logger.info(f"Using Chrome profile: {CUSTOM_PROFILE_PATH}")

                options.add_argument('--ignore-ssl-errors')
                options.add_argument('--ignore-certificate-errors')
                options.add_argument('--allow-running-insecure-content')
                options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36')
                
                # Don't use detach mode - we want to wait for browser closure
                # Keep the driver connected so we can detect when browser closes
                
                # Start Chrome driver
                driver = uc.Chrome(options=options)
                
                # Navigate to Instagram
                driver.get("https://www.instagram.com/")
                logger.info("Chrome opened and navigated to Instagram")
                
                # Take a screenshot like setup_chromev1.py
                try:
                    driver.save_screenshot('instagram_chrome_login.png')
                    logger.info("Captured screenshot of Instagram page")
                except Exception as e:
                    logger.error(f"Failed to capture screenshot: {e}")
                
                # Wait for user to manually log in and close the browser
                logger.info("Waiting for user to log in manually and close the browser...")
                
                try:
                    # Keep checking if the browser is still open
                    # This will block until the browser is closed or an error occurs
                    while True:
                        try:
                            # Try to get the current URL - this will fail if browser is closed
                            current_url = driver.current_url
                            time.sleep(2)  # Check every 2 seconds
                        except Exception as e:
                            # Browser was closed or connection lost
                            logger.info("Browser was closed by user")
                            break
                            
                except Exception as e:
                    logger.info(f"Browser session ended: {e}")
                
                finally:
                    # Ensure driver is properly closed
                    try:
                        driver.quit()
                    except:
                        pass
                
                # Now that browser is closed, update .env file
                logger.info("Browser closed, updating .env file with profile path...")
                update_env_file_with_profile(CUSTOM_PROFILE_PATH)
                
                # Set a flag to indicate login completion
                with open('chrome_login_complete.flag', 'w') as f:
                    f.write(f"Login completed at {datetime.now().isoformat()}")
                
                logger.info("Chrome login setup completed successfully")
                
            except Exception as e:
                logger.error(f"Error in integrated Chrome setup: {e}")
                # Set error flag
                with open('chrome_login_error.flag', 'w') as f:
                    f.write(f"Error: {str(e)}")
        
        def update_env_file_with_profile(profile_path):
            """Update the .env file with the custom profile path"""
            try:
                # Read existing .env file
                env_lines = []
                if os.path.exists('.env'):
                    with open('.env', 'r') as f:
                        env_lines = f.readlines()
                
                # Check if CHROME_PROFILE_PATH already exists
                profile_path_exists = False
                for i, line in enumerate(env_lines):
                    if line.startswith('CHROME_PROFILE_PATH='):
                        env_lines[i] = f'CHROME_PROFILE_PATH={profile_path}\n'
                        profile_path_exists = True
                        break
                
                # Add CHROME_PROFILE_PATH if it doesn't exist
                if not profile_path_exists:
                    env_lines.append(f'CHROME_PROFILE_PATH={profile_path}\n')
                
                # Write back to .env file
                with open('.env', 'w') as f:
                    f.writelines(env_lines)
                
                logger.info(f"Updated .env file with CHROME_PROFILE_PATH={profile_path}")
                
            except Exception as e:
                logger.error(f"Failed to update .env file: {e}")
        
        # Start Chrome setup in background thread
        setup_thread = threading.Thread(target=run_integrated_chrome_setup, daemon=True)
        setup_thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Chrome browser opened at Instagram. Please log in manually and close the browser when done.'
        })
        
    except Exception as e:
        logger.error(f"Error starting Chrome login setup: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/login/chrome_status')
def get_chrome_login_status():
    """Check the status of Chrome login process"""
    try:
        # Check for completion flag
        if os.path.exists('chrome_login_complete.flag'):
            return jsonify({
                'status': 'completed',
                'message': 'Login completed successfully! Your session has been saved.'
            })
        
        # Check for error flag
        if os.path.exists('chrome_login_error.flag'):
            with open('chrome_login_error.flag', 'r') as f:
                error_msg = f.read().strip()
            return jsonify({
                'status': 'error',
                'message': f'Login failed: {error_msg}'
            })
        
        # Neither flag exists - still in progress
        return jsonify({
            'status': 'in_progress',
            'message': 'Waiting for you to complete login and close the browser...'
        })
        
    except Exception as e:
        logger.error(f"Error checking Chrome login status: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Error checking status: {str(e)}'
        }), 500

@app.route('/health')
def health_check():
    """Health check endpoint for Docker"""
    try:
        # Basic health checks
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'services': {
                'flask': True,
                'vnc_available': False
            }
        }
        
        # Check VNC availability if possible
        try:
            from vnc_setup import vnc_manager
            health_status['services']['vnc_available'] = vnc_manager.check_system_compatibility()
        except:
            pass
            
        return jsonify(health_status), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Global scheduler manager
scheduler_manager = None

class SchedulerManager:
    """Manages the background scheduler thread"""
    
    def __init__(self):
        self.scheduler_thread = None
        self.stop_event = threading.Event()
        self.is_running = False
        self.poster = None
        
    def start_scheduler(self):
        """Start the scheduler in a background thread"""
        if self.is_running:
            logger.info("Scheduler is already running")
            return False
            
        self.stop_event.clear()
        self.is_running = True
        
        def run_scheduler():
            """Background scheduler function"""
            try:
                logger.info("Starting background scheduler thread")
                self.poster = InstagramPoster()
                
                # Import schedule here to avoid circular imports
                import schedule
                
                # Clear any existing jobs
                schedule.clear()
                
                # Track current settings to detect changes
                last_times = None
                last_timezone = None
                
                while not self.stop_event.is_set():
                    try:
                        # Reload settings to pick up any changes
                        self.poster.settings = self.poster.load_settings()
                        current_times = self.poster.get_setting('posting_times', ['09:00', '13:00', '17:00', '21:00'])
                        current_timezone = self.poster.get_setting('timezone', 'UTC')
                        
                        # Check if scheduler is disabled
                        if not self.poster.get_setting('enabled', True):
                            schedule.clear()
                            last_times = None
                            last_timezone = None
                            time.sleep(60)
                            continue
                        
                        # If settings changed, reschedule
                        if last_times != current_times or last_timezone != current_timezone:
                            schedule.clear()
                            
                            try:
                                # Convert user timezone times to server time and schedule
                                user_tz = pytz.timezone(current_timezone)
                                
                                # Automatically detect server timezone using system's local time
                                try:
                                    import datetime as dt
                                    system_tz = dt.datetime.now().astimezone().tzinfo
                                    server_tz_str = str(system_tz)
                                    
                                    if hasattr(system_tz, 'zone'):
                                        server_tz = system_tz
                                    else:
                                        try:
                                            import re
                                            tz_match = re.search(r'tzfile\(\'([^\']+)\'\)', server_tz_str)
                                            if tz_match:
                                                server_tz = pytz.timezone(tz_match.group(1))
                                            else:
                                                if server_tz_str in ['WAT']:
                                                    server_tz = pytz.timezone('Africa/Lagos')
                                                elif server_tz_str in ['PST']:
                                                    server_tz = pytz.timezone('US/Pacific')
                                                elif server_tz_str in ['EST']:
                                                    server_tz = pytz.timezone('US/Eastern')
                                                elif server_tz_str in ['UTC']:
                                                    server_tz = pytz.timezone('UTC')
                                                else:
                                                    offset = dt.datetime.now().astimezone().utcoffset()
                                                    hours_offset = offset.total_seconds() / 3600
                                                    
                                                    offset_to_tz = {
                                                        0: 'UTC',
                                                        1: 'Europe/Berlin',
                                                        -5: 'US/Eastern',
                                                        -8: 'US/Pacific',
                                                        8: 'Asia/Shanghai',
                                                        9: 'Asia/Tokyo',
                                                    }
                                                    
                                                    if hours_offset in offset_to_tz:
                                                        server_tz = pytz.timezone(offset_to_tz[hours_offset])
                                                    else:
                                                        server_tz = pytz.timezone('UTC')
                                        except:
                                            server_tz = pytz.timezone('UTC')
                                except:
                                    server_tz = pytz.timezone('UTC')
                                
                                # Get today's date for conversion
                                today = datetime.now().date()
                                
                                for time_str in current_times:
                                    try:
                                        hour, minute = map(int, time_str.split(':'))
                                        target_datetime = datetime.combine(today, datetime.min.time().replace(hour=hour, minute=minute))
                                        user_time = user_tz.localize(target_datetime)
                                        server_time = user_time.astimezone(server_tz)
                                        server_time_str = server_time.strftime("%H:%M")
                                        
                                        schedule.every().day.at(server_time_str).do(self.poster.post_monthly_content)
                                        logger.info(f"Scheduled posting: {time_str} {current_timezone} -> {server_time_str} server time")
                                    except Exception as e:
                                        logger.error(f"Error scheduling time {time_str}: {e}")
                                
                                last_times = current_times[:]
                                last_timezone = current_timezone
                                logger.info(f"Successfully scheduled {len(current_times)} posting times")
                                
                            except Exception as e:
                                logger.error(f"Timezone error: {e}. Using UTC as fallback.")
                        
                        # Run pending jobs
                        schedule.run_pending()
                        
                    except Exception as e:
                        logger.error(f"Error in scheduler loop: {e}")
                    
                    # Check for stop every 60 seconds
                    time.sleep(60)
                    
            except Exception as e:
                logger.error(f"Fatal error in scheduler thread: {e}")
            finally:
                logger.info("Scheduler thread stopped")
                self.is_running = False
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info("Scheduler thread started")
        return True
    
    def stop_scheduler(self):
        """Stop the scheduler thread"""
        if not self.is_running:
            logger.info("Scheduler is not running")
            return False
            
        logger.info("Stopping scheduler thread...")
        self.stop_event.set()
        
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
            
        self.is_running = False
        logger.info("Scheduler stopped")
        return True
    
    def get_status(self):
        """Get scheduler status"""
        return {
            'running': self.is_running,
            'thread_alive': self.scheduler_thread.is_alive() if self.scheduler_thread else False
        }

def initialize_scheduler():
    """Initialize and start the scheduler by default"""
    global scheduler_manager
    try:
        scheduler_manager = SchedulerManager()
        
        # Check if scheduler should be enabled by default
        settings_file = Path('scheduler_settings.json')
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    if settings.get('enabled', True):  # Default to True if not specified
                        logger.info("Starting scheduler automatically on app startup")
                        scheduler_manager.start_scheduler()
                    else:
                        logger.info("Scheduler is disabled in settings, not starting automatically")
            except Exception as e:
                logger.error(f"Error reading settings, starting scheduler anyway: {e}")
                scheduler_manager.start_scheduler()
        else:
            # No settings file, start scheduler with default settings
            logger.info("No settings file found, starting scheduler with defaults")
            scheduler_manager.start_scheduler()
            
    except Exception as e:
        logger.error(f"Error initializing scheduler: {e}")

def cleanup_scheduler():
    """Cleanup scheduler on app shutdown"""
    global scheduler_manager
    if scheduler_manager:
        logger.info("Shutting down scheduler...")
        scheduler_manager.stop_scheduler()

# Register cleanup function
atexit.register(cleanup_scheduler)

# Signal handlers for graceful shutdown
def signal_handler(sig, frame):
    logger.info(f"Received signal {sig}, shutting down gracefully...")
    cleanup_scheduler()
    exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

if __name__ == "__main__":
    # Create upload folder if it doesn't exist
    upload_folder = Path('content')
    upload_folder.mkdir(exist_ok=True)
    
    # Initialize scheduler
    initialize_scheduler()
    
    # Start the Flask app
    print("[LAUNCH] Starting Instagram Auto Poster Web Interface...")
    print("[MOBILE] Visit http://localhost:5000 to manage your content")
    print("[SETTINGS]  Scheduler will run automatically in the background")
    print("[STOP] Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=5003, debug=False) 