import asyncio
import tornado.web
import tornado.ioloop
import json
import re
from bson import ObjectId
from pymongo import AsyncMongoClient

UIds = "studente"
Pws = "ZPZfw5K6RWhOSani"
connection_string = "mongodb+srv://" + UIds + ":" + Pws + "@cluster0.geflqhy.mongodb.net/?appName=Cluster0"
client = AsyncMongoClient(connection_string)
db = client["apptask"]
prodotti_collection = db["tasks"]


class ProdottoListHandler(tornado.web.RequestHandler):
    async def get(self):
        prodotti = []
        cursor = prodotti_collection.find({})
        async for doc in cursor:
            prodotti.append({
                "id": str(doc["_id"]),
                "nome": doc["nome"],
                "prezzo": doc["prezzo"],
                "categoria": doc["categoria"],
                "stato": doc["stato"]
            })
        self.render("prodotti.html", prodotti=prodotti)

class NewProdottoHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("new_prodotto.html", message=None)

    async def post(self):
        nome = self.get_body_argument("nome")
        prezzo = self.get_body_argument("prezzo")
        categoria = self.get_body_argument("categoria")
        stato = self.get_body_argument("stato", default=None)


        await prodotti_collection.insert_one({
            "nome": nome,
            "prezzo": prezzo,
            "categoria": categoria,
            "stato": stato
        })
        self.redirect("/prodotti")

class DeleteProdottiHandler(tornado.web.RequestHandler):
    async def post(self, prodotto_id):
        await prodotti_collection.delete_one({"_id": ObjectId(prodotto_id)})
        self.redirect("/prodotti")

class ModificaProdottiHandler(tornado.web.RequestHandler):
    async def post(self, prodotto_id):
        prod = await prodotti_collection.find_one({"_id": ObjectId(prodotto_id)})

        nuovo_stato = "on"

        if prod["stato"] == "on":
            nuovo_stato="off"

        await prodotti_collection.update_one(
            {"_id": ObjectId(prodotto_id)},
            {"$set": {"stato": nuovo_stato}}
        )
        self.redirect("/prodotti")


class ProdottiAPIHandler(tornado.web.RequestHandler):
    async def get(self):
        prodotti = []
        cursor = prodotti_collection.find({})
        async for doc in cursor:
            prodotti.append({
                "id": str(doc["_id"]),
                "nome": doc["nome"],
                "prezzo": doc["prezzo"],
                "categoria": doc["categoria"],
                "stato": doc["stato"]
            })
        self.write({"tasks": prodotti})

    async def post(self):
        data = tornado.escape.json_decode(self.request.body)
        result = await prodotti_collection.insert_one({
            "title": data["title"],
            "completed": False
        })
        self.write({"id": str(result.inserted_id)})

class ProdottoAPIHandler(tornado.web.RequestHandler):
    async def delete(self, prodotto_id):
        await prodotti_collection.delete_one({"_id": ObjectId(prodotto_id)})
        self.write({"status": "deleted"})

class FiltraProdottiHandler(tornado.web.RequestHandler):
    async def post(self):
        categoriafiltro = self.get_body_argument("categoriafiltro", default=None)
        if categoriafiltro == "Filtro":
            categoriafiltro=None
        statofiltro = self.get_body_argument("statofiltro", default=None)
        print(statofiltro)
        cursore = []
        cursor = prodotti_collection.find({})
        prodotti = []

        async for doc in cursor:
            cursore.append({
                "id": str(doc["_id"]),
                "nome": doc["nome"],
                "prezzo": doc["prezzo"],
                "categoria": doc["categoria"],
                "stato": doc["stato"]
                })
            print(doc["stato"])

        if categoriafiltro != None:
            for i in cursore:
                if i["categoria"]==categoriafiltro and str(i["stato"])==str(statofiltro):
                    prodotti.append({
                        "id": str(i["id"]),
                        "nome": i["nome"],
                        "prezzo": i["prezzo"],
                        "categoria": i["categoria"],
                        "stato": i["stato"]
                    })

        else:
            for i in cursore:
                if str(i["stato"])==str(statofiltro):
                    prodotti.append({
                        "id": str(i["id"]),
                        "nome": i["nome"],
                        "prezzo": i["prezzo"],
                        "categoria": i["categoria"],
                        "stato": i["stato"]
                    })


        self.render("prodotti.html", prodotti=prodotti)




def make_app():
    return tornado.web.Application([
        (r"/prodotti", ProdottoListHandler),
        (r"/prodotti/new", NewProdottoHandler),
        (r"/prodotti/filtro", FiltraProdottiHandler),
        (r"/prodotti/delete/([0-9a-fA-F]+)", DeleteProdottiHandler),
        (r"/prodotti/modifica/([0-9a-fA-F]+)", ModificaProdottiHandler),

        (r"/api/prodotti", ProdottoAPIHandler),
        (r"/api/prodotti/([0-9a-fA-F]+)", ProdottoAPIHandler),

    ], )


async def main(shutdown_event):
    app = make_app()
    app.listen(8888)
    print("Server attivo su http://localhost:8888/prodotti")
    await shutdown_event.wait()
    print("Chiusura server...")

if __name__ == "__main__":
    shutdown_event = asyncio.Event()
    try:
        asyncio.run(main(shutdown_event))
    except KeyboardInterrupt:
        shutdown_event.set()
