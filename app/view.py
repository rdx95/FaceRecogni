from flask import render_template, request, redirect
from app import app



@app.route('/compare', methods=['GET','POST'])
def addnew():
    try:
        if request.method == 'POST':
            pass
        else :
            return render_template('chklabel.html')
    except :
        return ("An unexpected error ocurred")