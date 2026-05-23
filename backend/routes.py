from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db, Admin, Book, Member, Category, IssuedBook, Fine, BookRequest
from datetime import datetime, timedelta
from sqlalchemy import func
from config import Config

main = Blueprint('main', __name__)

# ── AUTH ──────────────────────────────────────────────────────────────────────

@main.route('/', methods=['GET', 'POST'])
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        admin = Admin.query.filter_by(username=request.form.get('username')).first()
        if admin and admin.check_password(request.form.get('password')):
            login_user(admin)
            flash('Welcome back!', 'success')
            return redirect(url_for('main.dashboard'))
        flash('Invalid credentials.', 'danger')
    return render_template('login.html')


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('main.login'))


# ── STUDENT LOGIN/PORTAL ──────────────────────────────────────────────────────

@main.route('/student', methods=['GET', 'POST'])
def student_login():
    if session.get('student_id'):
        return redirect(url_for('main.student_portal'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        member = Member.query.filter_by(email=email).first()
        if member and member.status == 'active':
            session['student_id'] = member.id
            session['student_name'] = member.name
            return redirect(url_for('main.student_portal'))
        flash('Email not found or account inactive.', 'danger')
    return render_template('student_login.html')


@main.route('/student/logout')
def student_logout():
    session.pop('student_id', None)
    session.pop('student_name', None)
    return redirect(url_for('main.student_login'))


@main.route('/student/portal')
def student_portal():
    if not session.get('student_id'):
        return redirect(url_for('main.student_login'))
    member = Member.query.get_or_404(session['student_id'])
    categories = Category.query.order_by(Category.name).all()
    cat_id = request.args.get('category', '')
    search = request.args.get('search', '')

    query = Book.query
    if cat_id:
        query = query.filter(Book.category_id == cat_id)
    if search:
        query = query.filter(db.or_(
            Book.title.ilike(f'%{search}%'),
            Book.author.ilike(f'%{search}%')
        ))
    books = query.order_by(Book.title).all()

    # Stock return dates
    stock_info = {}
    for b in books:
        if b.available_quantity == 0:
            earliest = IssuedBook.query.filter_by(
                book_id=b.id, status='issued'
            ).order_by(IssuedBook.due_date.asc()).first()
            if earliest:
                stock_info[b.id] = earliest.due_date.strftime('%d %b %Y')

    # Member's currently issued books
    my_books = IssuedBook.query.filter_by(
        member_id=member.id, status='issued'
    ).order_by(IssuedBook.due_date.asc()).all()

    # Member's fines
    my_fines = db.session.query(Fine).join(IssuedBook).filter(
        IssuedBook.member_id == member.id,
        Fine.paid == False
    ).all()

    # Member's requests
    my_requests = BookRequest.query.filter_by(
        member_id=member.id
    ).order_by(BookRequest.requested_at.desc()).all()

    # Books already requested (pending) by this member
    pending_book_ids = [r.book_id for r in my_requests if r.status == 'pending']

    return render_template('student_portal.html',
        member=member,
        categories=categories,
        books=books,
        stock_info=stock_info,
        my_books=my_books,
        my_fines=my_fines,
        my_requests=my_requests,
        pending_book_ids=pending_book_ids,
        category_filter=cat_id,
        search=search,
        datetime=datetime
    )


@main.route('/student/request/<int:book_id>', methods=['POST'])
def student_request_book(book_id):
    if not session.get('student_id'):
        return redirect(url_for('main.student_login'))
    member_id = session['student_id']

    # Check if already requested
    existing = BookRequest.query.filter_by(
        book_id=book_id, member_id=member_id, status='pending'
    ).first()
    if existing:
        flash('You already have a pending request for this book.', 'warning')
        return redirect(url_for('main.student_portal'))

    req = BookRequest(book_id=book_id, member_id=member_id)
    db.session.add(req)
    db.session.commit()
    flash('Book request submitted! The librarian will review it.', 'success')
    return redirect(url_for('main.student_portal'))


# ── DASHBOARD ─────────────────────────────────────────────────────────────────

@main.route('/dashboard')
@login_required
def dashboard():
    stats = {
        'total_books':    Book.query.count(),
        'available_books': db.session.query(func.sum(Book.available_quantity)).scalar() or 0,
        'issued_books':   IssuedBook.query.filter_by(status='issued').count(),
        'total_members':  Member.query.count(),
        'overdue_books':  IssuedBook.query.filter(
            IssuedBook.status == 'issued',
            IssuedBook.due_date < datetime.utcnow()
        ).count(),
        'total_fines':    db.session.query(func.sum(Fine.amount)).filter_by(paid=True).scalar() or 0,
    }
    recent_issues = IssuedBook.query.order_by(IssuedBook.issue_date.desc()).limit(5).all()
    category_data = db.session.query(Category.name, func.count(Book.id))\
        .join(Book, Book.category_id == Category.id).group_by(Category.name).all()
    monthly_data = db.session.query(
        func.month(IssuedBook.issue_date), func.count(IssuedBook.id)
    ).group_by(func.month(IssuedBook.issue_date)).all()
    pending_requests = BookRequest.query.filter_by(status='pending').count()

    return render_template('dashboard.html', **stats,
                           recent_issues=recent_issues,
                           category_data=category_data,
                           monthly_data=monthly_data,
                           pending_requests=pending_requests)


# ── BOOK REQUESTS (ADMIN) ─────────────────────────────────────────────────────

@main.route('/requests')
@login_required
def book_requests():
    pending  = BookRequest.query.filter_by(status='pending').order_by(BookRequest.requested_at.desc()).all()
    approved = BookRequest.query.filter_by(status='approved').order_by(BookRequest.reviewed_at.desc()).all()
    rejected = BookRequest.query.filter_by(status='rejected').order_by(BookRequest.reviewed_at.desc()).all()
    return render_template('requests.html', pending=pending, approved=approved, rejected=rejected)


@main.route('/requests/approve/<int:req_id>', methods=['POST'])
@login_required
def approve_request(req_id):
    req = BookRequest.query.get_or_404(req_id)
    req.status      = 'approved'
    req.reviewed_at = datetime.utcnow()
    req.admin_note  = request.form.get('note', '')
    db.session.commit()
    flash(f'Request approved for {req.member.name} — "{req.book.title}".', 'success')
    return redirect(url_for('main.book_requests'))


@main.route('/requests/reject/<int:req_id>', methods=['POST'])
@login_required
def reject_request(req_id):
    req = BookRequest.query.get_or_404(req_id)
    req.status      = 'rejected'
    req.reviewed_at = datetime.utcnow()
    req.admin_note  = request.form.get('note', '')
    db.session.commit()
    flash(f'Request rejected for {req.member.name}.', 'warning')
    return redirect(url_for('main.book_requests'))


# ── BOOKS ─────────────────────────────────────────────────────────────────────

@main.route('/books')
@login_required
def books():
    search   = request.args.get('search', '')
    cat_id   = request.args.get('category', '')
    page     = request.args.get('page', 1, type=int)
    query    = Book.query
    if search:
        query = query.filter(db.or_(
            Book.title.ilike(f'%{search}%'),
            Book.author.ilike(f'%{search}%'),
            Book.isbn.ilike(f'%{search}%')
        ))
    if cat_id:
        query = query.filter(Book.category_id == cat_id)
    books      = query.order_by(Book.title).paginate(page=page, per_page=10)
    categories = Category.query.order_by(Category.name).all()

    stock_info = {}
    for b in books.items:
        if b.available_quantity == 0:
            earliest = IssuedBook.query.filter_by(
                book_id=b.id, status='issued'
            ).order_by(IssuedBook.due_date.asc()).first()
            if earliest:
                stock_info[b.id] = earliest.due_date.strftime('%d %b %Y')

    return render_template('books.html', books=books, categories=categories,
                           search=search, category_filter=cat_id,
                           stock_info=stock_info)


@main.route('/books/add', methods=['POST'])
@login_required
def add_book():
    try:
        qty  = int(request.form['quantity'])
        book = Book(title=request.form['title'], author=request.form['author'],
                    isbn=request.form['isbn'],
                    publisher=request.form.get('publisher',''),
                    publish_year=request.form.get('publish_year') or None,
                    quantity=qty, available_quantity=qty,
                    category_id=int(request.form['category_id']))
        db.session.add(book)
        db.session.commit()
        flash('Book added!', 'success')
    except Exception as e:
        db.session.rollback(); flash(f'Error: {e}', 'danger')
    return redirect(url_for('main.books'))


@main.route('/books/edit/<int:bid>', methods=['POST'])
@login_required
def edit_book(bid):
    book = Book.query.get_or_404(bid)
    try:
        new_qty = int(request.form['quantity'])
        diff    = new_qty - book.quantity
        book.title        = request.form['title']
        book.author       = request.form['author']
        book.isbn         = request.form['isbn']
        book.publisher    = request.form.get('publisher','')
        book.publish_year = request.form.get('publish_year') or None
        book.quantity     = new_qty
        book.available_quantity = max(0, book.available_quantity + diff)
        book.category_id  = int(request.form['category_id'])
        db.session.commit()
        flash('Book updated!', 'success')
    except Exception as e:
        db.session.rollback(); flash(f'Error: {e}', 'danger')
    return redirect(url_for('main.books'))


@main.route('/books/delete/<int:bid>', methods=['POST'])
@login_required
def delete_book(bid):
    book = Book.query.get_or_404(bid)
    try:
        db.session.delete(book); db.session.commit()
        flash('Book deleted.', 'success')
    except Exception as e:
        db.session.rollback(); flash(f'Error: {e}', 'danger')
    return redirect(url_for('main.books'))


# ── CATEGORIES ────────────────────────────────────────────────────────────────

@main.route('/categories/add', methods=['POST'])
@login_required
def add_category():
    cat = Category(name=request.form['name'], description=request.form.get('description',''))
    db.session.add(cat); db.session.commit()
    flash('Category added!', 'success')
    return redirect(url_for('main.books'))


# ── MEMBERS ───────────────────────────────────────────────────────────────────

@main.route('/members')
@login_required
def members():
    search  = request.args.get('search', '')
    page    = request.args.get('page', 1, type=int)
    query   = Member.query
    if search:
        query = query.filter(db.or_(
            Member.name.ilike(f'%{search}%'),
            Member.email.ilike(f'%{search}%'),
            Member.phone.ilike(f'%{search}%')
        ))
    members = query.order_by(Member.name).paginate(page=page, per_page=10)
    return render_template('members.html', members=members, search=search)


@main.route('/members/add', methods=['POST'])
@login_required
def add_member():
    try:
        m = Member(name=request.form['name'], email=request.form['email'],
                   phone=request.form.get('phone',''),
                   department=request.form.get('department',''),
                   status=request.form.get('status','active'))
        db.session.add(m); db.session.commit()
        flash('Member added!', 'success')
    except Exception as e:
        db.session.rollback(); flash(f'Error: {e}', 'danger')
    return redirect(url_for('main.members'))


@main.route('/members/edit/<int:mid>', methods=['POST'])
@login_required
def edit_member(mid):
    m = Member.query.get_or_404(mid)
    try:
        m.name=request.form['name']; m.email=request.form['email']
        m.phone=request.form.get('phone',''); m.department=request.form.get('department','')
        m.status=request.form.get('status','active')
        db.session.commit(); flash('Member updated!', 'success')
    except Exception as e:
        db.session.rollback(); flash(f'Error: {e}', 'danger')
    return redirect(url_for('main.members'))


@main.route('/members/delete/<int:mid>', methods=['POST'])
@login_required
def delete_member(mid):
    m = Member.query.get_or_404(mid)
    try:
        db.session.delete(m); db.session.commit()
        flash('Member deleted.', 'success')
    except Exception as e:
        db.session.rollback(); flash(f'Error: {e}', 'danger')
    return redirect(url_for('main.members'))


# ── ISSUE / RETURN ────────────────────────────────────────────────────────────

@main.route('/issue-return')
@login_required
def issue_return():
    issued  = IssuedBook.query.filter_by(status='issued').order_by(IssuedBook.issue_date.desc()).all()
    books   = Book.query.filter(Book.available_quantity > 0).all()
    members = Member.query.filter_by(status='active').all()
    return render_template('issue_return.html', issued=issued, books=books, members=members)


@main.route('/issue', methods=['POST'])
@login_required
def issue_book():
    book   = Book.query.get_or_404(int(request.form['book_id']))
    member = Member.query.get_or_404(int(request.form['member_id']))
    if book.available_quantity < 1:
        flash('Book not available!', 'danger')
        return redirect(url_for('main.issue_return'))
    due = datetime.utcnow() + timedelta(days=Config.LOAN_PERIOD_DAYS)
    ib  = IssuedBook(book_id=book.id, member_id=member.id,
                     issue_date=datetime.utcnow(), due_date=due, status='issued')
    book.available_quantity -= 1
    db.session.add(ib); db.session.commit()
    flash(f'"{book.title}" issued to {member.name}. Due: {due.strftime("%d %b %Y")}', 'success')
    return redirect(url_for('main.issue_return'))


@main.route('/return/<int:ib_id>', methods=['POST'])
@login_required
def return_book(ib_id):
    ib = IssuedBook.query.get_or_404(ib_id)
    if ib.status == 'returned':
        flash('Already returned.', 'warning')
        return redirect(url_for('main.issue_return'))
    ib.return_date = datetime.utcnow()
    ib.status      = 'returned'
    ib.book.available_quantity += 1
    fine_amt = ib.calculate_fine()
    if fine_amt > 0:
        fine = Fine(issued_book_id=ib.id, amount=fine_amt, paid=False)
        db.session.add(fine)
        flash(f'Book returned. Fine of ₹{fine_amt} generated!', 'warning')
    else:
        flash('Book returned successfully!', 'success')
    db.session.commit()
    return redirect(url_for('main.issue_return'))


# ── FINES ─────────────────────────────────────────────────────────────────────

@main.route('/fines')
@login_required
def fines():
    all_fines = Fine.query.order_by(Fine.created_at.desc()).all()
    return render_template('fines.html', fines=all_fines)


@main.route('/fines/pay/<int:fine_id>', methods=['POST'])
@login_required
def pay_fine(fine_id):
    fine = Fine.query.get_or_404(fine_id)
    fine.paid = True; fine.paid_date = datetime.utcnow()
    db.session.commit()
    flash('Fine marked as paid!', 'success')
    return redirect(url_for('main.fines'))


# ── REPORTS ───────────────────────────────────────────────────────────────────

@main.route('/reports')
@login_required
def reports():
    issued_report   = IssuedBook.query.filter_by(status='issued').all()
    returned_report = IssuedBook.query.filter_by(status='returned').all()
    fine_report     = Fine.query.all()
    active_members  = Member.query.filter_by(status='active').all()
    return render_template('reports.html',
        issued_report=issued_report,
        returned_report=returned_report,
        fine_report=fine_report,
        active_members=active_members)


# ── API HELPERS ───────────────────────────────────────────────────────────────

@main.route('/api/book/<int:bid>')
@login_required
def api_book(bid):
    b = Book.query.get_or_404(bid)
    return jsonify({'id':b.id,'title':b.title,'author':b.author,
                    'isbn':b.isbn,'publisher':b.publisher,
                    'publish_year':b.publish_year,'quantity':b.quantity,
                    'available_quantity':b.available_quantity,
                    'category_id':b.category_id})


@main.route('/api/member/<int:mid>')
@login_required
def api_member(mid):
    m = Member.query.get_or_404(mid)
    return jsonify({'id':m.id,'name':m.name,'email':m.email,
                    'phone':m.phone,'department':m.department,'status':m.status})