# routes_chat.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import Group, GroupMessage

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/create_group', methods=['POST'])
@login_required
def create_group():
    if current_user.email != 'jayadm@gmail.com':
        return jsonify({'success': False, 'message': 'Você não tem permissão para criar grupos.'})

    if request.is_json:
        data = request.get_json()
        group_name = data['group_name']
        description = data['description']
        categories = ','.join(data['categories'])
    else:
        group_name = request.form['name']
        description = request.form['description']
        categories = ','.join(request.form.getlist('categories'))

    existing_group = Group.query.filter_by(name=group_name).first()
    if existing_group:
        if request.is_json:
            return jsonify({'success': False, 'message': 'Um grupo com este nome já existe.'})
        else:
            flash('Um grupo com este nome já existe.', 'danger')
            return redirect(url_for('chat.group_list'))

    new_group = Group(name=group_name, description=description, categories=categories, admin_id=current_user.id)
    new_group.members.append(current_user)
    new_group.member_count = 1

    db.session.add(new_group)
    db.session.commit()

    if request.is_json:
        return jsonify({'success': True, 'message': 'Grupo criado com sucesso!'})
    else:
        flash('Grupo criado com sucesso!', 'success')
        return redirect(url_for('chat.group_list'))


@chat_bp.route('/join_group/<int:group_id>')
@login_required
def join_group(group_id):
    group = Group.query.get_or_404(group_id)

    if current_user not in group.members:
        group.members.append(current_user)
        group.member_count += 1
        db.session.commit()
        flash(f'Você entrou no grupo {group.name}', 'success')

    return redirect(url_for('chat.group_chat', group_id=group_id))

@chat_bp.route('/group/<int:group_id>', methods=['GET', 'POST'])
@login_required
def group_chat(group_id):
    group = Group.query.get_or_404(group_id)

    if request.method == 'POST':
        message_content = request.form['message']
        new_message = GroupMessage(
            content=message_content,
            user=current_user,
            group=group
        )
        db.session.add(new_message)
        db.session.commit()
        return redirect(url_for('chat.group_chat', group_id=group_id))

    if current_user not in group.members:
        group.members.append(current_user)
        db.session.commit()

    messages = GroupMessage.query.filter_by(group_id=group_id).order_by(GroupMessage.date_posted).all()
    return render_template('group_chat.html', group=group, messages=messages, user=current_user)

@chat_bp.route('/groups')
@login_required
def group_list():
    groups = Group.query.all()
    return render_template('group_list.html', groups=groups, user=current_user)

@chat_bp.route('/main')
def main_page():
    groups = Group.query.all()
    return render_template('index.html', groups=groups, user=current_user)


@chat_bp.route('/edit_group/<int:group_id>', methods=['POST'])
@login_required
def edit_group(group_id):
    if current_user.email != 'jayadm@gmail.com':
        return jsonify({'success': False, 'message': 'Você não tem permissão para editar este grupo.'})

    group = Group.query.get_or_404(group_id)

    data = request.get_json()
    group.name = data['group_name']
    group.description = data['description']
    group.categories = ','.join(data['categories'])

    db.session.commit()

    return jsonify({'success': True, 'message': 'Grupo editado com sucesso!'})

@chat_bp.route('/delete_group/<int:group_id>', methods=['DELETE'])
@login_required
def delete_group(group_id):
    if current_user.email != 'jayadm@gmail.com':
        return jsonify({'success': False, 'message': 'Você não tem permissão para excluir este grupo.'})

    group = Group.query.get_or_404(group_id)

    # Excluir todas as mensagens do grupo
    GroupMessage.query.filter_by(group_id=group_id).delete()

    db.session.delete(group)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Grupo excluído com sucesso!'})
