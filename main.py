from flask import Flask, render_template

app=Flask(__name__)

@app.route('/',methods=['GET','POST'])
def home():
    return render_template('base.html')

@app.route('/submit',methods=['GET','POST'])
def submit():
    #I would add Langchain code here
    #For now it would just return 5
    scores=80
    return render_template('home.html',score=scores)

if __name__=='__main__':
    app.run(debug=True)