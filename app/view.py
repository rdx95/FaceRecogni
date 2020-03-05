from flask import render_template, request, redirect
from app import app


@app.route('/addnew', methods=['GET','POST'])
def addnew():
    if request.method == 'POST':
        pass
    else :
        return render_template('chklabel.html')