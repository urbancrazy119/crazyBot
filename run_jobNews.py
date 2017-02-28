import funcJob as f
import funcBot as b

PATH = '/usr/script/teleBot/log/'

msg = f.get_news()
if msg is not None:
    file = open(PATH+'job_execute.log','a')
    print >> file, msg
    file.close()
    b.broadcast_option('job',msg)
