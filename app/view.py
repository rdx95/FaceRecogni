from app import app
from flask import render_template, request, redirect


if __name__ == "__main__":
    app.run(host='0.0.0.0')


@app.route('/comparelabel', methods=['GET','POST'])
def addnew():
    if request.method == 'POST':
        pass
    else :
        return render_template('compare.html')