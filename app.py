from flask import Flask, jsonify, request
import json
import os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = 'courses.json'

# Ensure the JSON file exists at startup
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

def load_courses():
    """Load courses from the JSON file."""
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as e:
        return []

def save_courses(courses):
    """Save courses to the JSON file."""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(courses, f, indent=4)
    except IOError as e:
        raise Exception("Could not save courses to file.") from e

def find_course(course_id):
    """Find a course by its ID."""
    courses = load_courses()
    for course in courses:
        if course['id'] == course_id:
            return course
    return None

# Home route

@app.route('/')
def home():
    """Welcome message and API endpoints."""
    return jsonify({
        "message": "Welcome to CodeCraftHub API!",
        "available_api_endpoints": {
            "Add a New Course": "POST /api/courses",
            "Get All Courses": "GET /api/courses",
            "Get a Specific Course": "GET /api/courses/<course_id>",
            "Update a Course": "PUT /api/courses/<course_id>",
            "Delete a Course": "DELETE /api/courses/<course_id>"
        }
    }), 200

@app.route('/api/courses', methods=['POST'])
def add_course():
    """Add a new course."""
    data = request.json
    
    # Validate required fields
    if 'name' not in data or 'description' not in data or 'target_date' not in data or 'status' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    # Validate status
    valid_statuses = ['Not Started', 'In Progress', 'Completed']
    if data['status'] not in valid_statuses:
        return jsonify({'error': 'Invalid status value, must be one of: ' + ', '.join(valid_statuses)}), 400

    # Create a new course
    courses = load_courses()
    new_id = 1 if not courses else courses[-1]['id'] + 1
    new_course = {
        'id': new_id,
        'name': data['name'],
        'description': data['description'],
        'target_date': data['target_date'],
        'status': data['status'],
        'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    courses.append(new_course)
    save_courses(courses)
    
    return jsonify(new_course), 201

@app.route('/api/courses', methods=['GET'])
def get_courses():
    """Get all courses."""
    courses = load_courses()
    return jsonify(courses), 200

@app.route('/api/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    """Get a specific course by ID."""
    course = find_course(course_id)
    if course:
        return jsonify(course), 200
    return jsonify({'error': 'Course not found'}), 404

@app.route('/api/courses/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    """Update a course by ID."""
    data = request.json
    course = find_course(course_id)

    if not course:
        return jsonify({'error': 'Course not found'}), 404

    # Validate required fields
    if 'name' not in data or 'description' not in data or 'target_date' not in data or 'status' not in data:
        return jsonify({'error': 'Missing required fields'}), 400

    # Validate status
    valid_statuses = ['Not Started', 'In Progress', 'Completed']
    if data['status'] not in valid_statuses:
        return jsonify({'error': 'Invalid status value, must be one of: ' + ', '.join(valid_statuses)}), 400

    # Update course information
    course['name'] = data['name']
    course['description'] = data['description']
    course['target_date'] = data['target_date']
    course['status'] = data['status']
    
    # Save the updated course list
    courses = load_courses()
    save_courses(courses)


@app.route('/api/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    """Delete a course by ID."""
    courses = load_courses()
    course = find_course(course_id)

    if not course:
        return jsonify({'error': 'Course not found'}), 404

    courses.remove(course)  # Remove the course from the list
    save_courses(courses)    # Save the updated list

    return jsonify({'message': 'Course deleted', 'course': course}), 200

if __name__ == '__main__':
    app.run(debug=True)