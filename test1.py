# coding: utf-8

from flask import Flask, request, render_template
app = Flask(__name__)


@app.route("/")             # 网页根目录
def index():
    return 'Hello World!\n Method used: %s' % request.method  # 根目录内容，真正的网页不要直接返回html


@app.route("/<yourname>")
def hello(yourname):
    return '<h2>Hello %s </h2>' % yourname


@app.route("/bacon", methods=['GET', 'POST'])
def bacon():
    if request.method == 'POST':
        return 'You are using POST'
    else:
        return 'You are probably using GET'


@app.route('/profile/<name>')
def profile(name):
    return render_template('profile.html', name=name)


if __name__ == '__main__':
    app.run(debug=True)
