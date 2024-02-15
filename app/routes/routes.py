from bson import json_util
from flask import request, Response

from app import app
from app.middleware.auth_middleware import token_required
from app.modules.note.noteservice import NoteService
from app.modules.user.user_management import UserService


@app.route('/', methods=['GET'])
def hello():
    return 'Hello world'


#Authentication Services
# signup
@app.route('/signup', methods=['POST'])
def register():
    data = request.json
    if data is None or data == {}:
        return Response(response=json_util.dumps({"Error": "Please provide  information"}),
                        status=400, mimetype='application/json')
    response = UserService().register(data)
    return Response(response=json_util.dumps(response), status=200,
                    mimetype='application/json')

# login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if data is None or data == {}:
        return Response(response=json_util.dumps({"Error": "Please provide  information"}),
                        status=400, mimetype='application/json')
    response = UserService().login(data)
    return Response(response=json_util.dumps(response), status=200,
                    mimetype='application/json')



#Note Services
# only owner can share the note
@app.route('/notes/share', methods=['POST'])
@token_required
def share_note(current_user):
    data = request.json
    response = NoteService().share_note(data,current_user)
    return Response(response=json_util.dumps(response), status=200,
                    mimetype='application/json')


#only shared user and owner have access to view note
@app.route('/notes/<note_id>', methods=['GET'])  
@token_required
def get_one_note(current_user,note_id):
    print(note_id)
    response = NoteService.get_one_note(note_id,current_user)
    return Response(response=json_util.dumps(response), status=200,
                    mimetype='application/json')


#only admin has access to create a note
@app.route('/notes/create', methods=['POST'])  # Create MongoDB Document, through API and METHOD - POST
@token_required
def add_note(current_user):
    data = request.json
    response = NoteService.add_note(data,current_user)
    return Response(response=json_util.dumps(response), status=200,
                mimetype='application/json')
    
  
#only owner and shared users have access to update the note
@app.route('/notes/<note_id>', methods=['PUT']) 
@token_required    
def update_note(current_user,note_id):
    data = request.json
    print(data)
    print(note_id)
    response = NoteService.update_note(note_id,data,current_user)
    print(response)
    return Response(response=json_util.dumps(response), status=200,
                mimetype='application/json')
                 

#only owner user has access to delete the node
@app.route('/notes/<note_id>', methods=['DELETE']) 
@token_required    
def delete_note(current_user,note_id):
    response = NoteService.delete_note(note_id,current_user)
    return Response(response=json_util.dumps(response), status=200,
                mimetype='application/json')
    
# get version history only accesible by owner
@app.route('/notes/version-history/<note_id>', methods=['GET']) 
@token_required    
def version_history(current_user,note_id):
    response = NoteService.version_history(note_id,current_user)
    return Response(response=json_util.dumps(response), status=200,
                mimetype='application/json')
