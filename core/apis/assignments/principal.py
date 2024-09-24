from flask import Blueprint, json, request, jsonify
from core import db
from core.apis.assignments.schema import AssignmentGradeSchema, AssignmentSchema
from core.models.principals import Principal
from core.models.assignments import Assignment  # Assuming you have an ORM model for assignments


principal_bp = Blueprint('principal_assignments_resources', __name__)

def is_valid_principal(principal_data):
    try:
        # Parse the JSON data from the header
        principal_info = json.loads(principal_data)
        user_id = principal_info.get('user_id')
        principal_id = principal_info.get('principal_id')

        if not user_id or not principal_id:
            return False

        # Check if the principal exists in the database
        principal = Principal.query.filter_by(id=principal_id, user_id=user_id).first()

        return principal is not None

    except (json.JSONDecodeError, TypeError):
        return False
    



@principal_bp.route('/assignments', methods=['GET'])
def get_principal_assignments():
    # Check principal identity
    principal_data = request.headers.get('X-Principal')
    if not principal_data or not is_valid_principal(principal_data):
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Fetch all assignments (submitted or graded)
    assignments = Assignment.query.filter(Assignment.state.in_(['SUBMITTED', 'GRADED'])).all()

    # Serialize the assignment data
    result = []
    for assignment in assignments:
        result.append({
            "id": assignment.id,
            "content": assignment.content,
            "state": assignment.state,
            "student_id": assignment.student_id,
            "teacher_id": assignment.teacher_id,
            "created_at": assignment.created_at,
            "updated_at": assignment.updated_at,
            "grade": assignment.grade
        })
    
    return jsonify({"data": result})


@principal_bp.route('/teachers', methods=['GET'])
def get_teacher_assignments():
    """Fetch assignments by teacher"""
    # Check principal identity
    principal_data = request.headers.get('X-Principal')
    if not principal_data or not is_valid_principal(principal_data):
        return jsonify({'error': 'Unauthorized'}), 401

    # Extract user_id from principal data
    principal_info = json.loads(principal_data)
    user_id = principal_info.get('user_id')

    # Fetch assignments for the teacher
    assignments = Assignment.query.filter_by(teacher_id=user_id).all()

    # Prepare response in the required format
    result = []
    for assignment in assignments:
        result.append({
            "id": assignment.id,
            "user_id": assignment.teacher_id,  # Assuming user_id here corresponds to teacher_id
            "created_at": assignment.created_at,
            "updated_at": assignment.updated_at
        })
    
    return jsonify({"data": result})

@principal_bp.route('/assignments/grade', methods=['POST'])
def grade_assignment():
    """Grade an assignment"""
    # Check principal identity
    principal_data = request.headers.get('X-Principal')
    if not principal_data or not is_valid_principal(principal_data):
        return jsonify({'error': 'Unauthorized'}), 401

    # Validate and load the incoming payload
    incoming_payload = request.get_json()
    try:
        grade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

    # Fetch the assignment to be graded
    assignment = Assignment.query.get(grade_assignment_payload.id)
    if not assignment:
        return jsonify({'error': 'Assignment not found'}), 404

    # Validate the principal information from the header
    principal_info = json.loads(principal_data)
    principal_id = principal_info.get('principal_id')

    # Check if the principal is authorized to grade this assignment
    if assignment.teacher_id != Principal.query.filter_by(id=principal_id).first().user_id:
        return jsonify({'error': 'Unauthorized to grade this assignment'}), 403

    # Update the assignment's grade and state
    assignment.grade = grade_assignment_payload.grade
    assignment.state = 'GRADED'
    db.session.commit()

    # Serialize the updated assignment data
    graded_assignment_dump = AssignmentSchema().dump(assignment)
    return jsonify({"data": graded_assignment_dump})