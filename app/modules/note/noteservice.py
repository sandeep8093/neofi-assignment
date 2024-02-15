import json
from datetime import datetime
from bson.objectid import ObjectId
from flask import request, Response
from app.model.db import ConnectDB

class NoteService:
   
    @staticmethod
    def add_note(data,user):    
        try:
            connection = ConnectDB()
            mongodb_connection = connection.connect_db()
            notes = mongodb_connection.neofi["notes"]
            print(user)
            # Validated title and content
            if not data.get('title') or not data.get('content'):
                return {'error': 'Title and content are required fields'}
            
            # checking for duplicate note title
            existing_note = notes.find_one({"title": data['title'], "user_id": user['id']})
            if existing_note:
                return {'error': 'Note with this title already exists for the user'}
            
            # Adding user_id to the note data
            data['user_id'] = user['id']
            data['created_at'] = datetime.utcnow()

            notes.insert_one(data)
            output = {'status': 'Successfully Inserted', 'data': data}
            return output

        except Exception as e:
            print(e)
            return {'error': f'Failed to add note: {str(e)}'}

    @staticmethod
    def share_note(data,user):                 
        try:
            connection = ConnectDB()
            mongodb_connection = connection.connect_db()
            notes = mongodb_connection.neofi["notes"]
            note_id=data['note_id']
            shared_users = data['shared_users']

            obj_instance = ObjectId(note_id)

            # Retrieved the note to be shared
            note_to_share = notes.find_one({"_id": obj_instance})
            print(note_to_share)
            if not note_to_share:
                return {'error': 'Note not found'}, 404

            # Extracted the existing shared_users list or initialize it if not present
            existing_shared_users = note_to_share.get('shared_users', [])

            # Added new shared_users to the existing list
            for user_id in shared_users:
                if user_id not in existing_shared_users:
                    existing_shared_users.append(user_id)

            # Updated the note with the updated shared_users list
            notes.update_one(
                {"_id": obj_instance},
                {"$set": {"shared_users": existing_shared_users}}
            )

            return {'status': 'Note shared successfully', 'note_id': str(obj_instance)}

        except Exception as e:
            return {'error': f'Failed to share note: {str(e)}'}

    @staticmethod
    def get_one_note(note_id, user):
        try:
            connection = ConnectDB()
            mongodb_connection = connection.connect_db()
            notes = mongodb_connection.neofi["notes"]
            obj_instance = ObjectId(note_id)

            # Retrieved the note for the specified note_id and user_id
            document = notes.find_one({
                "_id": obj_instance,
                "$or": [
                    {"user_id": user['id']},  # Owner of the note
                    {"shared_users": {"$in": [user['id']]}}  # Shared users
                ]
            })

            if document:
                return {'requested_note': document}
            else:
                return {'note_not_found'}

        except Exception as e:
            return {'error': f'Failed to retrieve note: {str(e)}'}


    @staticmethod
    def update_note(note_id, data, user):
        try:
            connection = ConnectDB()
            mongodb_connection = connection.connect_db()
            notes = mongodb_connection.neofi["notes"]
            obj_instance = ObjectId(note_id)

            # Retrieved the existing note
            existing_note = notes.find_one({
                "_id": obj_instance,
                "$or": [
                    {"user_id": user['id']},  # Owner of the note
                    {"shared_users": {"$in": [user['id']]}}  # Shared users
                ]
            })

            if existing_note:
                # Got the existing content and timestamp
                existing_content = existing_note.get('content', '')
                existing_timestamps = existing_note.get('timestamps', [])

                # Appended the new sentences to the existing content
                new_content = existing_content + '\n' + data['content']

                # Added a timestamp for the update with previous and new content
                timestamp = datetime.utcnow()
                timestamp_data = {
                    'note_updated_by': user['id'],
                    'timestamp': timestamp,
                    'previous_content': existing_content,
                    'new_content': new_content
                }
                existing_timestamps.append(timestamp_data)

                # Updated the note with the new content and timestamps
                response = notes.update_one(
                    {"_id": obj_instance},
                    {
                        "$set": {'content': new_content, 'timestamps': existing_timestamps}
                    }
                )

                return {"status": "successfully_updated"}

            else:
                return {'error': 'Note not found or you do not have permission to update it'}

        except Exception as e:
            return {'error': f'Failed to update note: {str(e)}'}
      
    @staticmethod
    def delete_note(note_id, user):          
        try:
            connection = ConnectDB()
            mongodb_connection = connection.connect_db()
            notes = mongodb_connection.neofi["notes"]
            obj_instance = ObjectId(note_id)
            response = notes.delete_one({"_id": obj_instance, 'user_id': user['id']})
            return {"status": "successfully_deleted"}

        except Exception as e:
            return {'error': f'Failed to delete note: {str(e)}'}
    
    
    def get_changes_since_timestamp(self, note_id, timestamp):
        connection = ConnectDB()
        mongodb_connection = connection.connect_db()
        notes = mongodb_connection.neofi["notes"]

        # Retrieve the note content at the specified timestamp
        note_at_timestamp = notes.find_one(
            {"_id": note_id, "timestamps.timestamp": timestamp},
            {"content": 1, "_id": 0, "timestamps.$": 1}
        )

        # Retrieve the content changes made since the specified timestamp
        changes_since_timestamp = []
        
        if note_at_timestamp:
            current_content = note_at_timestamp.get('content', '')
            current_lines = current_content.split('\n')

            # Extracted the content and timestamp at the specified timestamp
            timestamp_data = note_at_timestamp.get('timestamps', [])[0]
            
            if timestamp_data:
                previous_content_lines = timestamp_data.get('previous_content', '').split('\n')
                current_lines1=timestamp_data.get('new_content', '').split('\n')
                min_length = min(len(current_lines1), len(previous_content_lines))

                # Compare each line from current_lines with the corresponding line in previous_content amd keeping the new change
                for line_number in range(1, min_length + 1):
                    current_line = current_lines1[line_number ]
                    previous_line = previous_content_lines[line_number - 1]
                 
                changes_since_timestamp.append({'line_number': line_number, 'change': current_line})
                    
        return changes_since_timestamp

    @staticmethod
    def version_history(note_id, user):          
        try:
            connection = ConnectDB()
            mongodb_connection = connection.connect_db()
            notes = mongodb_connection.neofi["notes"]
            obj_instance = ObjectId(note_id)

            # Retrieved the note with the specified note_id and current_user's access
            note = notes.find_one({"_id": obj_instance, 'user_id': user['id']})

            if not note:
                return {'error': 'Note not found or you do not have permission to access it'}, 404

            # Retrieved version history from timestamps and changes
            version_history = note.get('timestamps', [])
            
            for change in version_history:
                # Adding  changes made to the note at each timestamp
                change['changes'] = NoteService().get_changes_since_timestamp(obj_instance, change['timestamp'])
                    
            return {'version_history': version_history}

        except Exception as e:
            return {'error': f'Failed to retrieve version history: {str(e)}'}

            
