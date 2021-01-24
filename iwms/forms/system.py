from wtforms.validators import DataRequired
from app.admin.forms import AdminIndexForm, AdminEditForm, AdminField



class DepartmentEditForm(AdminEditForm):
    name = AdminField(label="Name",validators=[DataRequired()])

    def edit_fields(self):
        return [
            [self.name]
        ]
    edit_title = 'Edit department'


class DepartmentForm(AdminIndexForm):
    index_headers = ['Name','Created by','created at','updated by','updated at']
    index_title = 'Departments'
    
    name = AdminField(label="Name",validators=[DataRequired()])

    def create_fields(self):
        return [[self.name]]


class EmailForm(AdminIndexForm):
    index_headers = ['Module Code','Description','Type','Email Address']
    index_title = "Email Addresses"
    index_message = "User groups"

    email = AdminField(label='Email Address',input_type='email',validators=[DataRequired()])
    module_code = AdminField(label="Module Code",validators=[DataRequired()])
    description = AdminField(label="Description",required=False)
    type = AdminField(label='Type',validators=[DataRequired()])

    def create_fields(self):
        return [[self.email,self.module_code],[self.description,self.type]]


class EmailEditForm(AdminEditForm):
    email = AdminField(label='Email Address',input_type='email',validators=[DataRequired()])
    module_code = AdminField(label="Module Code",validators=[DataRequired()])
    description = AdminField(label="Description",required=False)
    type = AdminField(label='Type',validators=[DataRequired()])

    def edit_fields(self):
        return [
            [self.email,self.module_code],
            [self.description,self.type]
        ]
    edit_title = 'Edit email address'


class GroupForm(AdminIndexForm):
    index_headers = ['Group Name','created by','created at','updated by','updated at']
    index_title = "Groups"
    index_message = "User groups"

    name = AdminField(label="Name",validators=[DataRequired()])

    def create_fields(self):
        return [
            [self.name]
            ]

class GroupEditForm(AdminEditForm):
    name = AdminField(label='Name', validators=[DataRequired()])
    
    def edit_fields(self):
        return [[self.name]]

    edit_title = "Edit group"