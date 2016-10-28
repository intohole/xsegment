#coding=utf-8


import web
from b2 import system2
from xsegment.ZooSegment import MMSegment
urls =(
    "/cut.*","cut"
)

segment = MMSegment()
system2.reload_utf8()
class cut:


    def GET(self):
        user_data = web.input()
        content = user_data.content
        return " ".join(segment.segment(content))


app = web.application(urls, globals())


if __name__ == "__main__":

    app.run()
