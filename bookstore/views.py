#coding:utf-8
from django.shortcuts import render,render_to_response
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from bookstore.models import User
from django import forms
from django.views.decorators.csrf import csrf_exempt
import logging
from django.shortcuts import render,render_to_response
from django.http import HttpResponse,HttpResponseRedirect
from django.template import RequestContext
from django import forms
from bookstore.models import User
import MySQLdb
from bookstore.models import DB_Connection,Comment_Book_ID_Holder
from django.contrib import messages
from django.shortcuts import redirect
from datetime import datetime

#表单
class UserForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField()

@csrf_exempt

def general_parse(input_str):
    out=input_str.replace("'", "\\'")
    return out

#login page
def login(request):
    if request.method == 'POST': # If the form has been submitted...
        form = UserForm(request.POST) # A form bound to the POST data
        usrname = general_parse(request.POST['username'])
        usrpwd = general_parse(request.POST['userpwd'])
        conn = MySQLdb.connect(host=DB_Connection.host, user=DB_Connection.user, passwd=DB_Connection.pwd, db=DB_Connection.db,
                               charset=DB_Connection.charset)
        cursor = conn.cursor()
        #Select matched password#
        try:
            username_parsed = "\""+usrname+"\""
            statement = "SELECT password,User_type FROM Django_Bookstore.User WHERE UID = "+username_parsed
            logging.debug("DB statement:  "+statement)
            cursor.execute(statement)
            result = cursor.fetchall()
            if(result):
                for r in result:
                    if r[0] == usrpwd:
                        request.session['uid'] = usrname
                        request.session['user_type'] = r[1]
                        return redirect('/order')
                    else:
                        error_message = "Please input valid username and password!"
                        return render(request, 'login.html', {'alert': error_message})

            else:
                error_message = "Please input valid username and password!"
                return render(request, 'login.html', {'alert': error_message})
        except (MySQLdb.Error) as e:
            error_message = "Please input valid username and password!"
            return render(request, 'login.html', {'alert': error_message})
    else:
        form = UserForm() # An unbound form

    return render_to_response('login.html', {'form': form,})

#register page
def register(request):
    if request.method == 'POST': # If the form has been submitted...
        form = UserForm(request.POST) # A form bound to the POST data
        usrname = general_parse(request.POST['username'])
        usrpwd = general_parse(request.POST['userpwd'])
        logging.debug(usrname)
        logging.debug(usrpwd)
        conn = DB_Connection.conn

        cursor = conn.cursor()
        #Select matched password#
        try:
            data_user = (usrname,usrpwd,0)
            statement = "INSERT INTO Django_Bookstore.User(UID,Password,User_type) VALUES(%s, %s, %s)"
            cursor.execute(statement,data_user)
            conn.commit()
            cursor.close()
            conn.close()
            logging.debug("Cursor written, conn closed")
            success_message = "Registration finished! You may log in now!"
            return render(request,"register.html",{'alert': success_message})

        except (MySQLdb.Error) as e:
            logging.debug(e)
            error_message = "Duplicated user may found, try another username!"
            return render(request, 'register.html', {'alert': error_message})
    else:
        form = UserForm() # An unbound form

    return render_to_response('register.html', {'form': form,})


#parsed data as '%%'
def like_parsed(string):
    string = "%"+ string +"%"
    return string


#order page
def order(request):
    if request.method == 'POST' and 'request_type' in request.POST:
        req_tp = general_parse(request.POST['request_type'])
        if req_tp=='request_for_log_book_session':
            book_id = general_parse(request.POST['c_book_id'])
            request.session['book_id_for_comment']=book_id
            logging.debug('Book ID logged for comment')
            logging.debug(book_id)

    if request.method == 'POST' and 'Submit_Order' in request.POST:
        amount = int(request.POST['slct_amount'])
        book_id = general_parse(request.POST['c_book_id'])
        uid = request.session['uid']
        conn = MySQLdb.connect(host=DB_Connection.host, user=DB_Connection.user, passwd=DB_Connection.pwd, db=DB_Connection.db,
                               charset=DB_Connection.charset)
        cursor = conn.cursor()
        try:
            data_search = (book_id, uid, amount)
            statement = "INSERT INTO Django_Bookstore.Order (ISBN13, user_id, amount) VALUES (%s, %s, %s);"
            data_order = (amount,book_id)
            statement2 = "UPDATE Django_Bookstore.book SET copies = copies - %s WHERE ISBN13=%s;"
            cursor.execute(statement, data_search)
            conn.commit()
            cursor.execute(statement2, data_order)
            conn.commit()
            ##the mighty recommendation part#
            data_recommend = book_id
            statement3 = "SELECT * FROM Django_Bookstore.book WHERE ISBN13 IN (SELECT ISBN13  FROM Django_Bookstore.Order WHERE user_id IN (select user_id FROM Django_Bookstore.Order where ISBN13 = %s) group by isbn13);"
            cursor.execute(statement3, [data_recommend])
            conn.commit()
            result = cursor.fetchall()
            num_of_result = len(result)
            cursor.close()
            conn.close()
            success_message = "Order completed! You can check over order history page!"
            return render(request, "recommendation.html",{'result':result,'num_of_result':num_of_result,'alert': success_message})

        except (MySQLdb.Error) as e:
            logging.debug(e)
            error_message = "Error! Please input valid search submission"
            return render(request, 'order.html', {'alert': error_message})

    elif request.method == 'POST' and 'Submit_Search' in request.POST: # If the form has been submitted...
        form = UserForm(request.POST) # A form bound to the POST data
        booktitle = general_parse(request.POST['book_title'])
        bookauthor = general_parse(request.POST['book_author'])
        bookpublisher = general_parse(request.POST['book_publisher'])
        bookID = general_parse(request.POST['book_ID'])
        bookcat = general_parse(request.POST['book_cat'])
        bookyear = general_parse(request.POST['book_year'])
        sort_type = general_parse(request.POST['sort'])
        conn = MySQLdb.connect(host=DB_Connection.host, user=DB_Connection.user, passwd=DB_Connection.pwd, db=DB_Connection.db,
                               charset=DB_Connection.charset)
        cursor = conn.cursor()
        #Select result after search form submitted

        try:
            if sort_type=="Default":
                data_search = (
                like_parsed(booktitle), like_parsed(bookauthor), like_parsed(bookpublisher), like_parsed(bookID),
                like_parsed(bookcat), like_parsed(bookyear))
                statement = "SELECT * FROM Django_Bookstore.book WHERE title LIKE %s AND authors LIKE %s AND publisher LIKE %s AND ISBN13 LIKE %s AND book_type LIKE %s AND year LIKE %s;"
                # my_st = statement % data_user
                cursor.execute(statement, data_search)
                result = cursor.fetchall()
                num_of_result = len(result)
                cursor.close()
                conn.close()
                logging.debug("Data fetched, now try reload with new data")
                return render(request, "order_result.html", {'result': result, 'num_of_result': num_of_result})
            elif sort_type=="By Book Rating":
                data_search = (
                like_parsed(booktitle), like_parsed(bookauthor), like_parsed(bookpublisher), like_parsed(bookID),
                like_parsed(bookcat), like_parsed(bookyear))
                statement = "SELECT * FROM Django_Bookstore.book WHERE title LIKE %s AND authors LIKE %s AND publisher LIKE %s AND ISBN13 LIKE %s AND book_type LIKE %s AND year LIKE %s ORDER BY book_score desc;"
                # my_st = statement % data_user
                cursor.execute(statement, data_search)
                result = cursor.fetchall()
                num_of_result = len(result)
                cursor.close()
                conn.close()
                logging.debug("Data fetched, now try reload with new data")
                return render(request, "order_result.html", {'result': result, 'num_of_result': num_of_result})

        except (MySQLdb.Error) as e:
            logging.debug(e)
            error_message = "Error! Please input valid search info"
            return render(request, 'order_result.html', {'alert': error_message})

    else:
        form = UserForm() # An unbound form


    return render_to_response('order.html', {'form': form,})

def order_history(request):
    if request.method == 'POST' and 'request_type' in request.POST:
        req_tp = general_parse(request.POST['request_type'])
        if req_tp=='request_for_log_comment_book_id':
            book_id = general_parse(request.POST['c_book_id'])
            Comment_Book_ID_Holder.book_id=book_id
            logging.debug('Comment_book_id logged')

    if request.method == 'POST' and 'Submit_Comment' in request.POST:
        uid = request.session['uid']
        slct_book_id = Comment_Book_ID_Holder.book_id
        comment_content = general_parse(request.POST['comment'])
        rating = general_parse(request.POST['rating'])
        conn = MySQLdb.connect(host=DB_Connection.host, user=DB_Connection.user, passwd=DB_Connection.pwd, db=DB_Connection.db,
                               charset=DB_Connection.charset)
        cursor = conn.cursor()
        try:
            data_comment = (slct_book_id,comment_content,rating,uid)
            statement = "INSERT INTO Django_Bookstore.Comment (Book_id, Comment, Book_Rating, uid) VALUES ('%s', '%s', '%s', '%s');"
            st = statement % data_comment
            data_add_to_book = (rating,slct_book_id)
            statement2 = "UPDATE Django_Bookstore.book SET book_score=Django_Bookstore.book.book_score + '%s' WHERE ISBN13='%s';"
            st2 = statement2 % data_add_to_book
            cursor.execute(st)
            conn.commit()
            cursor.execute(st2)
            conn.commit()
            cursor.close()
            conn.close()
            success_message = "Comment submitted!"
            return render(request, "order.html", {'alert': success_message})
            #return redirect('/my_order_history')
        except (MySQLdb.Error) as e:
            error_message = "Please note that you can only submit one comment and rating for each book"
            return render(request, 'order.html', {'alert': error_message})

    else:
        form = UserForm()  # An unbound form

    uid = request.session['uid']
    conn = MySQLdb.connect(host=DB_Connection.host, user=DB_Connection.user, passwd=DB_Connection.pwd,
                           db=DB_Connection.db,
                           charset=DB_Connection.charset)
    cursor = conn.cursor()
    try:
        data_my_order_his = (uid)
        statement = "SELECT br.ISBN13, bs.title, bs.authors, bs.publisher, bs.year, br.amount, br.id_Order FROM Django_Bookstore.book as bs, Django_Bookstore.Order as br WHERE br.user_id='%s' and br.ISBN13=bs.ISBN13"
        my_st = statement % data_my_order_his
        #logging.debug(my_st)
        cursor.execute(my_st)
        result = cursor.fetchall()
        num_of_result = len(result)
        cursor.close()
        conn.close()
        logging.debug("Data fetched, now try reload with new data")
        return render(request,"my_order_history.html",{'result':result,'num_of_result':num_of_result,'form':form})
    except (MySQLdb.Error) as e:
        logging.debug(e)
        error_message = "Error! Please input valid search info"
        return render(request, 'my_order_history.html', {'alert': error_message,'form':form})


def user_info_float(request):
    if request.method == 'POST' and 'Submit_User_Update' in request.POST:
        uid = request.session['uid']
        real_name = general_parse(request.POST['real_name'])
        old_pwd = general_parse(request.POST['old_password'])
        new_pwd = general_parse(request.POST['new_password'])
        phone_num = general_parse(request.POST['phone_num'])
        conn = MySQLdb.connect(host=DB_Connection.host, user=DB_Connection.user, passwd=DB_Connection.pwd,
                               db=DB_Connection.db,
                               charset=DB_Connection.charset)
        cursor = conn.cursor()
        try:
            data_validate_user = (uid)
            statement = "SELECT Password FROM Django_Bookstore.User WHERE UID ='%s'"
            my_st = statement % data_validate_user
            cursor.execute(my_st)
            result = cursor.fetchall()
            if(result):
                for row in result:
                    for data in row:
                        if data == old_pwd:
                            try:
                                data_user = (new_pwd, real_name, phone_num, uid)
                                statement = "UPDATE Django_Bookstore.User SET Password='%s', real_name='%s', phone_num='%s' WHERE UID='%s'"
                                my_st = statement % data_user
                                cursor.execute(my_st)
                                conn.commit()
                                cursor.close()
                                conn.close()
                                done_alert = 'New user info logged'
                                logging.debug('User info flushed')
                                return render(request, 'User_info.html', {'alert': done_alert})
                            except (MySQLdb.Error) as e:
                                logging.debug(e)
                                error_message = "Error! Please input valid info"
                                return render(request, 'User_info.html', {'alert': error_message})
                        else:
                            error_message = "Please input valid old password to show you are the valid user!"
                            return render(request, 'User_info.html', {'alert': error_message})
        except (MySQLdb.Error) as e:
            logging.debug(e)
            error_message = "Error! Please input valid info"
            return render(request, 'User_info.html', {'alert': error_message})

    else:
        uid = request.session['uid']
        conn = MySQLdb.connect(host=DB_Connection.host, user=DB_Connection.user, passwd=DB_Connection.pwd,
                               db=DB_Connection.db,
                               charset=DB_Connection.charset)
        cursor = conn.cursor()
        try:
            data_user = (uid)
            statement = "SELECT * FROM Django_Bookstore.User WHERE UID ='%s'"
            my_st = statement % data_user
            cursor.execute(my_st)
            result = cursor.fetchall()
            for r in result:
                uid = r[0]
                pwd = r[1]
                user_type = r[2]
                user_real_name = r[3]
                user_phone_num = r[4]
                user_info_data = [uid, pwd, user_type, user_real_name, user_phone_num]
            logging.debug('User info flushed')
            return render(request, 'User_info.html', {'user_info': user_info_data})
        except (MySQLdb.Error) as e:
            logging.debug(e)
            error_message = "Error! Please input valid info"
            return render(request, 'User_info.html', {'alert': error_message})

    return render_to_response('User_info.html')


def comment(request):
    if request.method == 'POST' and 'request_type' in request.POST:
        req_tp = general_parse(request.POST['request_type'])
        if req_tp=='request_for_update_comment_score':
            book_id = request.session['book_id_for_comment']
            conn = MySQLdb.connect(host=DB_Connection.host, user=DB_Connection.user, passwd=DB_Connection.pwd,
                                   db=DB_Connection.db,
                                   charset=DB_Connection.charset)
            cursor = conn.cursor()
            cm_Book_id = request.POST['c_book_id']
            cm_uid = request.POST['my_uid']
            cm_score = request.POST['my_score']
            current_uid = request.session['uid']

            # Check if allowed:
            data_check_allowed = (cm_Book_id,cm_uid)
            statement = "SELECT Comment_uids FROM Django_Bookstore.Comment WHERE Book_id='%s' and uid='%s';"
            my_st = statement%data_check_allowed
            cursor.execute(my_st)
            result = cursor.fetchall()
            comment_uids = ""
            for r in result:
                comment_uids=r[0]

            # if in
            if current_uid not in comment_uids:
                try:
                    new_comment_uids = comment_uids + '&?#' + current_uid
                    data_updating = (cm_score, new_comment_uids, cm_Book_id, cm_uid)
                    statement2 = "UPDATE Django_Bookstore.Comment SET Comment_Rating=Django_Bookstore.Comment.Comment_Rating +'%s', Comment_uids='%s' WHERE Book_id='%s' and uid='%s';"
                    my_st2 = statement2 % data_updating
                    cursor.execute(my_st2)
                    conn.commit()
                    cursor.close()
                    conn.close()
                    success_message = "Comment is successfully rated!"
                    return render(request, 'comment.html', {'alert': success_message})

                except (MySQLdb.Error) as e:
                    logging.debug(e)
                    error_message = "Error! Connection problem!"
                    return render(request, 'comment.html', {'alert': error_message})

            if current_uid in comment_uids:
                cursor.close()
                conn.close()
                error_message = "Error! You commented to this post already!"
                return render(request, 'comment.html', {'alert': error_message})
    else:
        form = UserForm()  # An unbound form

    uid = request.session['uid']
    book_id = request.session['book_id_for_comment']
    conn = MySQLdb.connect(host=DB_Connection.host, user=DB_Connection.user, passwd=DB_Connection.pwd,
                           db=DB_Connection.db,
                           charset=DB_Connection.charset)
    cursor = conn.cursor()
    data_comment = (book_id)
    statement = "SELECT Comment,uid,Book_id,Comment_Rating FROM Django_Bookstore.Comment WHERE Book_id = '%s';"
    myst = statement % data_comment
    cursor.execute(myst)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return render(request, 'comment.html', {'result': result})



    #return render_to_response('comment.html')


def my_comment(request):
    uid = request.session['uid']
    conn = MySQLdb.connect(host=DB_Connection.host, user=DB_Connection.user, passwd=DB_Connection.pwd,
                           db=DB_Connection.db,
                           charset=DB_Connection.charset)
    cursor = conn.cursor()
    data_mycomment = (uid)
    statement = "SELECT Comment,Book_id FROM Django_Bookstore.Comment WHERE uid = '%s';"
    myst = statement%data_mycomment
    cursor.execute(myst)
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return render(request, 'my_comment.html', {'result': result})



def all_order_history(request):
    if request.session['user_type']==1:
        conn = MySQLdb.connect(host=DB_Connection.host, user=DB_Connection.user, passwd=DB_Connection.pwd,
                               db=DB_Connection.db,
                               charset=DB_Connection.charset)
        cursor = conn.cursor()
        try:
            statement = "SELECT * FROM Django_Bookstore.Order;"
            cursor.execute(statement)
            result = cursor.fetchall()
            num_of_result = len(result)
            cursor.close()
            conn.close()
            logging.debug("Data fetched, now try reload with new data")
            return render(request, 'all_order_history.html', {'result': result, 'num_of_result': num_of_result})
        except (MySQLdb.Error) as e:
            logging.debug(e)
            error_message = "Error! Please input valid search info"
            return render(request, 'all_order_history.html', {'alert': error_message})
    else:
        error_message = "No authority to enter!"
        return render(request, 'order.html', {'alert': error_message})

def create_books(request):
    if request.session['user_type']==1:
        if request.method == 'POST' and 'Submit_Create_Book' in request.POST: # If the form has been submitted...
            booktitle = general_parse(request.POST['book_title'])
            bookauthor = general_parse(request.POST['book_author'])
            bookpublisher = general_parse(request.POST['book_publisher'])
            bookID = general_parse(request.POST['book_ID'])
            bookcat = general_parse(request.POST['book_cat'])
            bookyear = general_parse(request.POST['book_year'])
            bookisbn10 = general_parse(request.POST['book_isbn10'])
            bookformat = general_parse(request.POST['book_format'])
            bookcopies = general_parse(request.POST['book_copies'])
            bookpages = general_parse(request.POST['book_pages'])
            booklan = general_parse(request.POST['book_lan'])
            conn = MySQLdb.connect(host=DB_Connection.host, user=DB_Connection.user, passwd=DB_Connection.pwd,
                                   db=DB_Connection.db,
                                   charset=DB_Connection.charset)
            cursor = conn.cursor()
            try:
                data_create_book = (booktitle,bookformat,bookpages,booklan,bookauthor,bookpublisher,bookyear,bookisbn10,bookID,bookcopies,bookcat)
                statement = "INSERT INTO Django_Bookstore.book(title, format, pages, language, authors, publisher, year, ISBN10, ISBN13, copies,book_type) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%s', '%s', '%s');"
                my_st = statement%data_create_book
                cursor.execute(my_st)
                conn.commit()
                data_add_to_record = (bookID,bookcopies)
                statement2 = "INSERT INTO Django_Bookstore.Arrival_history (ISBN13, Amount) VALUES ('%s', '%s');"
                my_st2 = statement2%data_add_to_record
                cursor.execute(my_st2)
                conn.commit()
                cursor.close()
                conn.close()
                done_alert = 'New book entry created'
                return render(request, 'create_book.html', {'alert': done_alert})
            except (MySQLdb.Error) as e:
                logging.debug(e)
                error_message = "Error! Please input valid info"
                return render(request, 'create_book.html', {'alert': error_message})
        else:
            form = UserForm()

        return render_to_response('create_book.html', {'form': form})
    else:
        error_message = "No authority to enter!"
        return render(request, 'order.html', {'alert': error_message})

def add_book(request):
    if request.session['user_type']==1:
        if request.method == 'POST' and 'Submit_Add_Book' in request.POST: # If the form has been submitted...
            bookID = general_parse(request.POST['book_ID'])
            amount = general_parse(request.POST['add_amunt'])
            conn = MySQLdb.connect(host=DB_Connection.host, user=DB_Connection.user, passwd=DB_Connection.pwd,
                                   db=DB_Connection.db,
                                   charset=DB_Connection.charset)
            cursor = conn.cursor()
            try:
                data_add_book = (amount,bookID)
                statement ="UPDATE Django_Bookstore.book SET copies=Django_Bookstore.book.copies+'%s' WHERE ISBN13='%s';"
                my_st = statement%data_add_book
                cursor.execute(my_st)
                conn.commit()
                data_add_to_record = (bookID,amount)
                statement2 = "INSERT INTO Django_Bookstore.Arrival_history (ISBN13, Amount) VALUES ('%s', '%s');"
                my_st2 = statement2%data_add_to_record
                cursor.execute(my_st2)
                conn.commit()
                cursor.close()
                conn.close()
                done_alert = 'Copies added'
                return render(request, 'add_book.html', {'alert': done_alert})
            except (MySQLdb.Error) as e:
                logging.debug(e)
                error_message = "Error! Please input valid info"
                return render(request, 'add_book.html', {'alert': error_message})
        else:
            form = UserForm()

        return render_to_response('add_book.html', {'form': form})
    else:
        error_message = "No authority to enter!"
        return render(request, 'order.html', {'alert': error_message})

def fill_blamk_for_list(mylist):
    size = len(mylist)
    margin = 5-size
    if size<5:
        for i in range(margin):
            mylist.append('')
    return mylist

def admin_panel(request):
    if request.session['user_type']==1:
        conn = MySQLdb.connect(host=DB_Connection.host, user=DB_Connection.user, passwd=DB_Connection.pwd,
                               db=DB_Connection.db,
                               charset=DB_Connection.charset)
        cursor = conn.cursor()
        try:
            # For Headers
            total_book_st = "SELECT COUNT(*) FROM Django_Bookstore.book;"
            total_comment_st = "SELECT COUNT(*) FROM Django_Bookstore.Comment;"
            total_order_st = "SELECT COUNT(*) FROM Django_Bookstore.Order;"
            total_user_st = "SELECT COUNT(*) FROM Django_Bookstore.User;"
            headers_list=[]
            cursor.execute(total_book_st)
            result = cursor.fetchall()
            for r in result:
                headers_list.append(r[0])
            cursor.execute(total_order_st)
            result = cursor.fetchall()
            for r in result:
                headers_list.append(r[0])
            cursor.execute(total_user_st)
            result = cursor.fetchall()
            for r in result:
                headers_list.append(r[0])
            cursor.execute(total_comment_st)
            result = cursor.fetchall()
            for r in result:
                headers_list.append(r[0])

            # For body
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            time_start = current_time[:8]+'01 00:00:00'
            time_end = current_time[:8]+'31 00:00:00'
            data_time = (time_start,time_end)
            author_statement = "SELECT t1.authors, COUNT(*) FROM Django_Bookstore.book t1, Django_Bookstore.Order t2 WHERE t2.order_time>='%s' and t2.order_time<='%s' and t1.ISBN13=t2.ISBN13 GROUP BY authors ORDER BY COUNT(*) desc LIMIT 5"
            book_statement = "SELECT title FROM book WHERE ISBN13 IN (SELECT ISBN13 FROM Django_Bookstore.Order WHERE order_time>='%s' and order_time<='%s' GROUP BY ISBN13) LIMIT 5"
            publisher_statement = "SELECT t1.publisher, COUNT(*) FROM Django_Bookstore.book t1, Django_Bookstore.Order t2 WHERE t2.order_time>='%s' and t2.order_time<='%s' and t1.ISBN13=t2.ISBN13 GROUP BY publisher ORDER BY COUNT(*) desc LIMIT 5"
            b_st = book_statement%data_time
            au_st = author_statement%data_time
            pub_st = publisher_statement%data_time

            cursor.execute(au_st)
            result = cursor.fetchall()
            best_author_list=[]
            for r in result:
                best_author_list.append(r[0])

            cursor.execute(b_st)
            result = cursor.fetchall()
            best_book_list=[]
            for r in result:
                best_book_list.append(r[0])

            cursor.execute(b_st)
            result = cursor.fetchall()
            best_publisher_list=[]
            for r in result:
                best_publisher_list.append(r[0])

            best_publisher_list=fill_blamk_for_list(best_publisher_list)
            best_book_list=fill_blamk_for_list(best_book_list)
            best_author_list=fill_blamk_for_list(best_author_list)

            cursor.close()
            conn.close()

            return render(request, 'admin_panel.html',{'pub_list':best_publisher_list, 'author_list': best_author_list, 'book_list':best_book_list, 'headers_list':headers_list})
        except (MySQLdb.Error) as e:
            logging.debug(e)
            error_message = "Error! Please input valid info"
            return render(request, 'add_book.html', {'alert': error_message})

    else:
        error_message = "No authority to enter!"
        return render(request, 'order.html', {'alert': error_message})