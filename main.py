from flask import Flask, render_template

app=Flask(__name__)

@app.route('/',methods=['GET','POST'])
def home():
    return render_template('home.html')

@app.route('/submit',methods=['GET','POST'])
def submit():
    #I would add Langchain code here
    #For now it would just return 5
    return '<h1>5</h1>'

if __name__=='__main__':
    app.run(debug=True)