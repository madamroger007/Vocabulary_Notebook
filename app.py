from flask import Flask, render_template, redirect, url_for, jsonify,request
import requests
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
# api_key = 'bd162044-b13e-4f3d-9606-fdfa81953b98'
# url = f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={api_key}"
# word = "potato"

app = Flask(__name__)
cxn_str = "mongodb+srv://adam:adamsjr123@coba.posdf04.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(cxn_str)

db = client.dbsparta_plus_week2

# Page Layout
@app.route("/")
def Main():
    word_result = db.words.find({},{"_id":False})
    words = []
    for word in word_result:
        definition = word['definitions'][0]['shortdef']
        definitions = definition if type(definition) is str else definition[0]
        words.append({
            'word': word['word'],
            'definition': definitions,

        })
    msg = request.args.get("msg")
    keyword = request.args.get("keyword")
    suggestions = request.args.get("suggestions")
    return render_template("index.html", words=words, msg=msg, keyword=keyword, suggestions=suggestions)


@app.route("/detail/<keyword>")
def Detail(keyword):
    api_key = "bd162044-b13e-4f3d-9606-fdfa81953b98"
    url = f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{keyword}?key={api_key}"
    response = requests.get(url)
    definitions = response.json()
    if not definitions:
        return redirect(url_for(
            'NotFound',
            msg = f'Could not find the Word { keyword }',
            keyword=keyword
        ))

    if type(definitions[0]) is str:
        suggestions = ', '.join(definitions)
        return redirect(url_for(
            'NotFound',
            msg = f'Could not find the Word,"{keyword}"did you mean',
            suggestions = suggestions,
            keyword=keyword
        ))

    status = request.args.get('status_give', 'new')
    return render_template("detail.html", word=keyword, definitions=definitions, status=status)

@app.route("/undefined")
def NotFound():
    msg = request.args.get("msg")
    keyword = request.args.get("keyword")
    suggestions = request.args.get("suggestions")
    return render_template("error404.html", msg=msg, keyword=keyword, suggestions=suggestions)


# Action
@app.route("/api/save_word", methods=["POST"])
def Save_word():
    json_data = request.get_json()
    word = json_data.get('word_give')
    definitions = json_data.get('definitions_give')

    doc = {
        'word': word,
        'definitions': definitions,
        'date': datetime.now().strftime('%Y%m%d') 
    }

    db.words.insert_one(doc)
    return jsonify({"result": "success", "msg": f"the word, {word} was saved"})


@app.route("/api/delete_word", methods=["POST"])
def Delete_word():
    word = request.form.get('word_give')
    db.words.delete_one({'word':word})
    db.examples.delete_many({'word':word})

    return jsonify({"result": "success", "msg": f"the word, {word} was delete"})

@app.route('/api/get_ex', methods=['GET'])
def Get_exs():
    word = request.args.get('word_give')
    example_data = db.examples.find({'word':word})
    examples = []
    for example in example_data:
        examples.append({
            'example': example.get('example'),
            'id': str(example.get("_id")),

        })
    print(examples)
    return jsonify({'result':'success',"examples": examples})

@app.route('/api/save_ex', methods=['POST'])
def Save_exs():
    word = request.form.get('word')
    example = request.form.get('example')
    doc = {
        'word': word,
        'example': example
    }
    db.examples.insert_one(doc)
    return jsonify({'result':'success',"msg": f"Your example was, {example}, saved!"})

@app.route('/api/delete_ex', methods=['POST'])
def Delete_exs():
    id = request.form.get('id')
    word = request.form.get('word')
    db.examples.delete_one({'_id': ObjectId(id)})
    return jsonify({'result':'success', "msg": f"Yout word, {word}, was deleted "})

if __name__ == "__main__":
    app.run(debug=True)
