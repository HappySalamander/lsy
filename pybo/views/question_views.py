from datetime import datetime

from flask import Blueprint, render_template, request, url_for, g, flash
from werkzeug.utils import redirect

from .. import db
from ..model import Question, Answer, User, question_voter
from ..forms import QuestionForm, AnswerForm
from pybo.views.auth_views import login_required
from sqlalchemy import func

bp = Blueprint('question', __name__, url_prefix='/question')


@bp.route('/list/')
def _list():
    page = request.args.get('page', type=int, default=1)
    kw = request.args.get('kw', type=str, default='')
    so = request.args.get('so', type=str, default='recent')
    ca = request.args.get('ca', type=str, default='')

    if so == 'recommend':
        sub_query = db.session.query(
            question_voter.c.question_id, func.count('*').label('num_voter')) \
            .group_by(question_voter.c.question_id).subquery()
        question_list = Question.query \
            .outerjoin(sub_query, Question.id == sub_query.c.question_id) \
            .order_by(sub_query.c.num_voter.desc(), Question.create_date.desc())
    elif so == 'popular':
        sub_query = db.session.query(
            Answer.question_id, func.count('*').label('num_answer')) \
            .group_by(Answer.question_id).subquery()
        question_list = Question.query \
            .outerjoin(sub_query, Question.id == sub_query.c.question_id) \
            .order_by(sub_query.c.num_answer.desc(), Question.create_date.desc())
    elif so == 'old':
        question_list = Question.query.order_by(Question.create_date.asc())

    elif so == 'recent':
        question_list = Question.query.order_by(Question.create_date.desc())
    else:
        question_list = Question.query.order_by(Question.create_date.desc())


    if ca == 'CU':
        question_list = Question.query.filter_by(category='CU')

    elif ca == 'GS25':
        question_list = Question.query.filter_by(category='GS25')
    elif ca == '미니스탑':
        question_list = Question.query.filter_by(category='미니스탑')

    elif ca == '세븐일레븐':
        question_list = Question.query.filter_by(category='세븐일레븐')
    else:
        question_list = Question.query.order_by(Question.create_date.desc())

    if kw:
        search = '%%{}%%'.format(kw)
        sub_query = db.session.query(Answer.question_id, Answer.content, User.username) \
            .join(User, Answer.user_id == User.id).subquery()
        question_list = question_list \
            .join(User) \
            .outerjoin(sub_query, sub_query.c.question_id == Question.id) \
            .filter(Question.subject.ilike(search) |  # 질문제목
                    Question.category.ilike(search) |  # 질문카테고리
                    Question.content.ilike(search) |  # 질문내용
                    User.username.ilike(search) |  # 질문작성자
                    sub_query.c.content.ilike(search) |  # 답변내용
                    sub_query.c.username.ilike(search)  # 답변작성자
                    ) \
            .distinct()
    question_list = question_list.paginate(page, per_page=10)
    return render_template('question/question_list.html', question_list=question_list, page=page, kw=kw, so=so, ca=ca)


@bp.route('/detail/<int:question_id>/')
def detail(question_id):
    # page = request.args.get('page', type=int, default=1)
    form = AnswerForm()
    question = Question.query.get_or_404(question_id)
    answer_list = Answer.query.order_by(Answer.create_date.desc())
    # answer_list = answer_list.paginate(page, per_page=10)
    return render_template('question/question_detail.html', question=question, answer_list=answer_list, form=form)


@bp.route('/create/', methods=('GET', 'POST'))
@login_required
def create():
    form = QuestionForm()
    if request.method == 'POST' and form.validate_on_submit():
        question = Question(subject=form.subject.data, category=form.category.data, content=form.content.data, create_date=datetime.now(),
                            user=g.user)

        db.session.add(question)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('question/question_form.html', form=form)
        # # 파일 업로드
        # titleimg = request.files['title_image']
        # fn = secure_filename(titleimg.filename)
        # if not fn:  # 파일이 없으면
        #     fn = 'dummy-image.jpg'
        # else:
        #     ######같은 이름 파일 업로드 중복처리.
        #     _ = 0
        #     while os.path.isfile("app/static/img/" + fn):
        #         fn = str(_) + fn
        #         _ += 1
        #     titleimg.save(os.path.join('app/static/img/' + fn))
        #
        # # print(title,password,contents,request.remote_addr,session.get('userid'))
        # db_class = dbModule.Database()  # db연결
        #
        # userid = session.get('userid')
        # sql = "SELECT name from user where id=%s;"
        # username = db_class.executeAll(sql, userid)  # username 받아오기
        #
        # sql = "INSERT INTO board (pwd, name, title, content, ip, viewcnt, titleimg) VALUES (%s, %s, %s, %s, %s, %s, %s);"
        # args = (password, username[0]['name'], title, contents, request.remote_addr, 0, fn)
        #
        # # print(args)
        # boards = db_class.executeAll(sql, args)
        # db_class.commit()
        # return redirect('/')
        #




@bp.route('/modify/<int:question_id>', methods=('GET', 'POST'))
@login_required
def modify(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user != question.user:
        flash('수정권한이 없습니다')
        return redirect(url_for('question.detail', question_id=question_id))
    if request.method == 'POST':  # POST 요청
        form = QuestionForm()
        if form.validate_on_submit():
            form.populate_obj(question)
            question.modify_date = datetime.now()  # 수정일시 저장
            db.session.commit()
            return redirect(url_for('question.detail', question_id=question_id))
    else:  # GET 요청
        form = QuestionForm(obj=question)
    return render_template('question/question_form.html', form=form)


# ## 글 수정하기
# @main.route('/update', methods=['GET', 'POST'])
# def update():
#     if 'userid' not in session:
#         # print("비로그인 상태")
#         return "<script>alert(\'로그인 후 이용하세요.\');document.location.href=\"login_service/login\"</script>"
#
#     # print("로그인 상태")
#     db_class = dbModule.Database()  # db연결
#     bid = request.args.get('bid')
#     if request.method == 'GET':
#         if request.args.get('bid') != None and bid != '':
#             sql = "SELECT * FROM board WHERE id=%s;"
#             old_board = db_class.executeAll(sql, bid)
#             return render_template('/main/update.html', old_board=old_board[0])
#
#     # POST
#     title = request.form['title']
#     contents = request.form['contents']
#     password = request.form['password']
#     if title == '' or password == '' or contents == '':
#         return "<script>alert(\'* 은 필수입력입니다.\');window.history.back();</script>"
#
#     sql = "SELECT pwd, titleimg FROM board WHERE id=%s;"
#     old_board = db_class.executeAll(sql, bid)
#     if old_board[0]['pwd'] != password:
#         return "<script>alert(\'비밀번호가 일치하지않습니다.\');window.history.back();</script>"
#
#     titleimg = request.files['title_image']  # 파일 업로드, 글 수정시 이전파일 삭제 후 업로드
#     fn = secure_filename(titleimg.filename)
#     print(old_board, fn, titleimg.filename)
#     if old_board[0]['titleimg'] != '' and old_board[0]['titleimg'] != None and old_board[0][
#         'titleimg'] != 'dummy-image.jpg' and fn:  # 이미 파일이 있을때 업로드
#         os.remove('app/static/img/' + old_board[0]['titleimg'])
#
#     ######같은 이름 파일 업로드 중복처리.
#     if fn:
#         _ = 0
#         while os.path.isfile("app/static/img/" + fn):
#             fn = str(_) + fn
#             _ += 1
#         titleimg.save(os.path.join('app/static/img/' + fn))
#         sql = "UPDATE board SET title=%s, content=%s, titleimg=%s WHERE id=%s;"
#         args = (title, contents, fn, bid)
#     else:
#         sql = "UPDATE board SET title=%s, content=%s WHERE id=%s;"
#         args = (title, contents, bid)
#     boards = db_class.executeAll(sql, args)
#     db_class.commit()
#
#     sql = "SELECT * FROM board WHERE id=%s;"
#     board = db_class.executeAll(sql, bid)
#     return render_template('/main/board.html', board=board[0], num=bid)



@bp.route('/delete/<int:question_id>')
@login_required
def delete(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user != question.user:
        flash('삭제권한이 없습니다')
        return redirect(url_for('question.detail', question_id=question_id))
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('question._list'))


@bp.route('/vote/<int:question_id>/')
@login_required
def vote(question_id):
    _question = Question.query.get_or_404(question_id)
    if g.user == _question.user:
        flash('본인이 작성한 글은 추천할수 없습니다')
    else:
        _question.voter.append(g.user)
        db.session.commit()
    return redirect(url_for('question.detail', question_id=question_id))
