from flask import Flask, render_template

app=Flask(__name__)

@app.route('/',methods=['GET','POST'])
def home():
    return render_template('base.html')

@app.route('/submit',methods=['GET','POST'])
def submit():
    return '<h1>5</h1>'

if __name__=='__main__':
    app.run(debug=True)