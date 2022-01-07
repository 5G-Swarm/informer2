from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def index():
    # 往模板中传入的数据
    my_str = 'Hello Word'
    my_int = 10
    my_array = [3, 4, 2, 1, 7, 9]
    my_dict = {
        'name': 'xiaoming',
        'age': 18
    }
    return render_template('index.html',
                           my_str=my_str,
                           my_int=my_int,
                           my_array=my_array,
                           my_dict=my_dict
                           )

#rendering the HTML page which has the button
# @app.route('/json')
# def json():
#     return render_template('json.html')

#background process happening without any refreshing
@app.route('/background_process_test')
def background_process_test():
    print("Hello\n\n\n\n")
    return ""

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug = True)