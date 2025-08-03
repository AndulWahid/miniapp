from flask import Flask, request, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# In-memory storage for filters (since Vercel doesn't allow file writes)
FILTERS_STORAGE = {
    "lax_pickup_active": True,
    "lax_dropoff_active": True,
    "monday_transfer_active": True,
    "tuesday_transfer_active": True,
    "wednesday_transfer_active": True,
    "thursday_transfer_active": True,
    "friday_transfer_active": True,
    "saturday_transfer_active": True,
    "sunday_transfer_active": True
}

@app.route('/api/update_filters_direct', methods=['POST'])
def update_filters_direct():
    """Direct API endpoint to update filters"""
    try:
        data = request.get_json()
        filters = data.get('filters', {})
        
        # Validate the filters structure
        required_keys = [
            'lax_pickup_active', 'lax_dropoff_active',
            'monday_transfer_active', 'tuesday_transfer_active',
            'wednesday_transfer_active', 'thursday_transfer_active',
            'friday_transfer_active', 'saturday_transfer_active',
            'sunday_transfer_active'
        ]
        
        for key in required_keys:
            if key not in filters:
                return jsonify({'success': False, 'error': f'Missing required key: {key}'}), 400
        
        # Update the in-memory storage
        global FILTERS_STORAGE
        FILTERS_STORAGE.update(filters)
        
        # Log the update
        print(f"[{datetime.now()}] Filters updated: {filters}")
        
        return jsonify({
            'success': True,
            'message': 'Filters updated successfully!',
            'filters': filters,
            'note': 'Filters are stored in memory. Copy the JSON below to update your bot file.'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/get_filters', methods=['GET'])
def get_filters():
    """Get current filter settings"""
    try:
        return jsonify({'success': True, 'filters': FILTERS_STORAGE})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/status', methods=['GET'])
def status():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'filters': FILTERS_STORAGE
    })

# Booked Slots API endpoints
@app.route('/api/schedule', methods=['GET'])
def get_schedule():
    """Get current schedule"""
    try:
        # In-memory storage for schedule (since Vercel doesn't allow file writes)
        SCHEDULE_STORAGE = {
            "booked_slots": [],
            "current_schedule": []
        }
        return jsonify({'success': True, 'schedule': SCHEDULE_STORAGE})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/booked_slots', methods=['GET'])
def get_booked_slots():
    """Get booked slots"""
    try:
        # In-memory storage for booked slots
        BOOKED_SLOTS_STORAGE = []
        return jsonify({'success': True, 'booked_slots': BOOKED_SLOTS_STORAGE})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/booked_slots', methods=['POST'])
def add_booked_slot():
    """Add a booked slot"""
    try:
        data = request.get_json()
        slot = data.get('slot', {})
        
        # Validate slot data
        required_keys = ['date', 'time', 'location', 'type']
        for key in required_keys:
            if key not in slot:
                return jsonify({'success': False, 'error': f'Missing required key: {key}'}), 400
        
        # In a real implementation, you would save to database
        # For now, just return success
        print(f"[{datetime.now()}] Booked slot added: {slot}")
        
        return jsonify({
            'success': True,
            'message': 'Booked slot added successfully!',
            'slot': slot
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/booked_slot', methods=['POST'])
def add_booked_slot_singular():
    """Add a booked slot (singular endpoint for compatibility)"""
    try:
        data = request.get_json()
        from_time = data.get('from', '')
        to_time = data.get('to', '')
        info = data.get('info', '')
        
        if not from_time or not to_time:
            return jsonify({'success': False, 'error': 'Start and end times are required'}), 400
        
        # Create slot object
        slot = {
            'from': from_time,
            'to': to_time,
            'info': info,
            'created_at': datetime.now().isoformat()
        }
        
        # In a real implementation, you would save to database
        # For now, just return success
        print(f"[{datetime.now()}] Booked slot added: {slot}")
        
        return jsonify({
            'success': True,
            'message': 'Slot added successfully!',
            'slot': slot
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/custom_filters', methods=['GET'])
def get_custom_filters():
    """Get custom filters (for compatibility with existing bot)"""
    try:
        return jsonify({'success': True, 'filters': FILTERS_STORAGE})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# For local development
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 
