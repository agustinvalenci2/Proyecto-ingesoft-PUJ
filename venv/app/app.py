from flask import (
    Flask,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for
)

import database

import autoincremental
import datetime
P=[]
hoy=datetime.date.today
database.connect()
tempdie=None
stf=lambda x:datetime.datetime.strptime(x,"%Y-%m-%d").date()
class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'

class Historia:
    def __init__(self, id, username, historia):
        self.id = id
        self.username = username
        self.historia= [historia]

    def __repr__(self):
        return f'<User: {self.username}>'
users = []
users.append(User(id=1, username='anonimo', password='jeje'))
users.append(User(id=2, username='bantu', password='crick'))
users.append(User(id=3, username='ivan', password='f'))
lista1=["paciente","medico","fecha","motivo","observaciones","talla","peso","historialfamiliar"
]
lista2=["colesterol","LDHcolesterol","HDLcolesterol","glucosa","c_reactiva","HgA1c"]

historias=[]
historias.append(Historia(111,'aa','casa'))
historias.append(Historia(112,'aa','casa2'))
historias.append(Historia(113 ,'aa','casa3'))
app = Flask(__name__)
app.secret_key = '3141592'
tempdoc=None
temptipo=None
nume=0
tipoo=0

@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']]
        if len(user)>0:
            g.user = user[0]

        
@app.route('/', methods = ['GET', 'POST'])
def login():

    if request.method == 'POST':

        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']
        q="select password,doc,admin from user where username ='{}'".format(username)

        ans = database.session.execute(q)
        if not(not ans):
            Password,Id,admin=ans[0]
            if Password == password:
                users.append(User(Id,username,Password))
                session['user_id'] = Id
                if not admin:
                    return redirect(url_for('profile'))
                else:
                    return redirect(url_for('adminp'))
        else:
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/profile',methods=['GET', 'POST'])
def profile():
    global fechas,medico,temptipo,tempdoc,nume,tipoo
    fechas=[]
    medico=[]
    
    if request.method == 'POST':
        if request.form.get("bs")=="1":
            num=int(request.form.get("search"))
            tipo=int(request.form.get("tipo"))
            B=request.form.get("inf")
            A=request.form.get("sup")
            print(A,B)
            tipo = 0 if tipo==None else tipo
            q1="select * from persona where doc ={} and tipo ={} ALLOW FILTERING".format(num,tipo)

            q2="select id,fecha,medico from historia where pacid ={} and tipo ={} ALLOW FILTERING".format(num,tipo)
            q3="select count(*) from paciente where id ={} and tipo ={} ALLOW FILTERING".format(num,tipo)
            for aaa in database.session.execute(q3):
                r1=aaa.count

            
            session['doc']=num
            session['tipo']=tipo
            if num!='' and tipo!='':
                print(num,tipo,r1,not r1)
                if r1==0:
                    tempdoc=num
                    temptipo=tipo
                    
                    return redirect(url_for('agregarpersona'))
                r2=sorted(database.session.execute(q2), key=lambda x:tuple(x)[1])
                if B!='':
                    r2=[i for i in r2 if i[1].date()<=stf(B)]
                if A!='':
                    r2=[i for i in r2 if stf(A)<=i[1].date()]
              
                ids=[i for i,x,y in r2]
                fechas=[x for i,x,y in r2]
                medico=[y for i,x,y in r2]
                tempdoc=num
                temptipo=tipo
                session['ids']=ids
                
                

                return redirect(url_for('hist'))
            else:
                return redirect(url_for('profile'))
            if request.form.get("lo")=="1":
                g.user=None
                return redirect(url_for('login'))
        if not g.user:
            return redirect(url_for('login'))

    return render_template('profile.html',nume=session.get('doc'),tipoo=session.get('tipo'))


@app.route('/hist',methods=['GET', 'POST'])

def hist():
    global temptipo,tempdoc
    if request.method == 'POST':

        if request.form.get("lo")=="1":
            g.user=None
            return redirect(url_for('profile'))
        if request.form.get("new")=="1":
            return redirect(url_for('newhist'))
        if request.form.get("his[]")!= None:
            session['historia']=request.form.get("his[]")
            return redirect(url_for("historia"))
        if request.form.get("fa")=="1":
            q="update persona2 set fallecimiento=toTimeStamp('{}') where documento={} and tipo={}".format(hoy(),session['doc'],session['tipo'])
            print(q)
            database.query(q)
            return redirect(url_for("profile"))
    return render_template('hist.html',fechas=fechas,medico = medico,ids=session.get('ids'))

@app.route('/adminp',methods=['GET', 'POST'])

def adminp():
    if request.method == 'POST':
        if request.form.get("admin")=="1":
            return redirect(url_for('admin'))
        elif request.form.get("medico")=="1":
            return redirect(url_for('profile'))
    return render_template("adminp.html")

@app.route('/admin',methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get("agregar")=='1':
            return redirect(url_for('agregarcuenta'))
        elif request.form.get("borrar")=='1':
            return redirect(url_for('borrarcuenta'))
        elif request.form.get("lo")=='1':
            return redirect(url_for('adminp'))
        
    return render_template("admin.html")


@app.route('/borrarcuenta',methods=['GET', 'POST'])
def borrarcuenta():
    if request.method == 'POST':
        if request.form.get("boton")=='1':
            U=request.form.get("username")
            if session['user_id']==int(U):
                q="delete from user where username ='{}'".format(U)
                database.session.execute(q)
                return redirect(url_for('agregarcuenta'))
            else:
                return redirect(url_for('borrarcuenta'))
        if request.form.get("agregar")=='1':
            return redirect(url_for('agregarcuenta'))
    return render_template("borrarcuenta.html")


@app.route('/agregarcuenta',methods=['GET', 'POST'])
def agregarcuenta():
    esp=database.query("select * from especialidad")
    if request.method == 'POST':
        if request.form.get("boton")=='1':
            U=request.form.get("username")
            P=request.form.get("password")
            I=request.form.get("ID")
            A=request.form.get("admin")
            E=request.form.getlist("espe[]")
            E=map(int,E)
            if len(P)>=10 and len(U)>0 :
                for e in E:
                    q="insert into auxesp (id,especialidades) values ({},{})".format(I,e)
                    database.query(q)
                A=A if A!=None else "0"
                A=bool(int(A))
                q="insert into medico (docid,id,espe) values ({},{},{})".format(I,I,I)
                database.session.execute(q)
                q="insert into user (username,password,doc,admin) values ('{}','{}',{},{})".format(U,P,I,A)
                database.session.execute(q)
            else:
                return redirect(url_for('agregarcuenta'))
        elif request.form.get("borrar")=='1':
            return redirect(url_for('borrarcuenta'))
    return render_template("agregarcuenta.html",esp=esp)

@app.route('/agregarpersona',methods=['GET', 'POST'])
def agregarpersona():
    global tempdoc,temptipo,nume,tipoo,temp
    E=database.query("select id,nombre from EPS")
    A=database.query("select id,alergia from alergias")
    if request.method == 'POST':
        nombre=request.form.get("name")
        apellido=request.form.get("ape")
        documento=session['doc']
        
        tipo=session['tipo']
        fecha=request.form.get("nac")
        mail=request.form.get("mail")
        EPS=request.form.get("EPS")
        telefono=request.form.get("tel")
        if nombre!='' and apellido !='' and documento !='' and tipo!='':
            if request.form.get("h")=='1':
                
                
                q2="insert into persona (documento,tipo,nombre,apellido,nacimiento,fallecimiento,mail,telefono) values({},{},'{}','{}','{}',{},'{}','{}')".format(documento,tipo,nombre,apellido,str(fecha),"null",mail,int(telefono))
                database.query(q2)
                
                
                li=map(int,request.form.getlist("alergia[]"))
                
                for al in li:
                    q="insert into auxalergias (id,alergias) values ({},{})".format(documento,al)
                    database.query(q)
                q="insert into paciente (id,tipo,EPS) values ({},{},{})".format(documento,tipo,EPS)
                database.query(q)
                nume=documento
                session['doc']=tipo
                return redirect(url_for('profile'))
            if request.form.get("lo")=='1':
                return redirect(url_for('profile'))
        else:
            return redirect(url_for('agregarpersona'))
    return render_template("agregarpersona.html",EPS=E,alergias=A)    


@app.route('/newhist',methods=['GET', 'POST'])
def newhist():
    global tempdoc,temptipo
    id=autoincremental.newid()
    print(tempdoc,temptipo)
    doc=tempdoc
    tipo=temptipo
    fecha=hoy()
    q="select * from medicacion"
    A=database.query(q)
    die=database.query("select * from dieta")
    E=database.query("select * from enfermedades")
    npre=0
    if request.method == 'POST':
        if request.form.get("ok")=='1':
            motivo=request.form.get("motivo")
            observaciones=request.form.get("observaciones")
            medico=motivo=request.form.get("medico")
            talla=request.form.get("talla")
            peso=request.form.get("peso")
            me=map(int,request.form.getlist("medicina[]"))
            en=map(int,request.form.getlist("enfermedades[]"))
            for i in me:
                q="insert into auxmedicina (id,medicina) values({},{})".format(id,i)
                database.query(q)
            for i in en:
                q="insert into enfermedades (id,endermedad) values({},{})".format(id,i)
                database.query(q)
            dieta=request.form.get("dieta") if session.get('die') == None else session['die']
            if  dieta=='-1':
                return redirect(url_for('dieta'))
            colesterol=request.form.get("colesterol")
            LDH=request.form.get("LDHcolesterol")
            HDL=request.form.get("HDLcolesterol")
            gluco=request.form.get("gluco")
            c_reac=request.form.get("c_reac")
            HgA1c=request.form.get("HgA1c")
            historial=request.form.get("historial")
            if request.form.get("pre")=='1':
                session['histemp']=(motivo,observaciones,medico,talla,peso,dieta,colesterol,LDH,HDL,gluco,c_reac,Hga1c,historial,dieta)
            if talla!="" and peso!="" and LDH !="" and HDL!="" and gluco !="" and c_reac !="" and HgA1c!="":
                q="""insert into historia (id,pacid,tipo,medico,fecha,motivo,observaciones,talla,peso,medicaciones,dieta,enfermedades,pregunta,historialfamiliar,resultados)
                 values ({},{},{},{},'{}','{}','{}',{},{},{},{},{},{},'{}',{})""".format(id,doc,tipo,medico,fecha,motivo,observaciones,talla,peso,id,dieta,id,id,historial,id)
                q2=""" insert into resultados (colesterol,LDHcolesterol,HDLcolesterol,gluco,c_reac,HgA1c) values({},{},{},{},{},{})""".format(colesterol,LDH,HDL,gluco,c_reac,HgA1c)
                database.query(q)
                if session.get('preguntas')!= None and len(session.get('preguntas'))!=0:

                    for pregunta,respuesta in session.get('preguntas'):
                        database.query("insert into preguntas (id,historia,pregunta) values ({},{},'{}')".format(autoincremental.newid(),id,pregunta))
                        database.query(("insert into respuestas (id,pregunta,respuesta) values ({},{},'{}')".format(id,id,respuesta)))
                    session['preguntas']=[]
                if request.form.get("preguntas")=='1':
                    session['preguntas']=[]
                    return redirect(url_for('preguntas'))        
                if request.form.get("lo")=='1':
                    return redirect(url_for('hist'))
            else:
                return redirect(url_for('newhist')) 
        
    return render_template("newhist.html",A=A,die=die,E=E,npre=npre,h=session.get('histemp'))

@app.route('/dieta',methods=['GET', 'POST'])
def dieta():
    global tempdie
    
    id=autoincremental.newid()
    session['die']=id
    q="select * from comida"
    C=database.query(q)
    if request.method == 'POST':
        if request.form.get("lo")=='1':
            return redirect(url_for('hist'))
        recomentaciones=request.form.get("recomentaciones")
        req=map(int,request.form.getlist("requerida[]"))
        evi=map(int,request.form.getlist("evitadas[]"))
        for i in req:
            q="insert into requerida (id,comida) values({},'{}')".format(id,i)
            database.query(q)
        for i in evi:
            q="insert into evitar (id,comida) values({},'{}'')".format(id,i)
            database.query(q)
    return render_template("newhist.html",C=C)

@app.route('/historia',methods=['GET', 'POST'])
def historia():
    
    q1="select pacid,medico,fecha,motivo,observaciones,talla,peso,historialfamiliar from historia where id={}".format(session['historia'])
    re=[]
    ev=[]
    a=list(database.query(q1))

    if len(a)>=1:
        a=list(a[0])
    else:
        a=[]
    
    
    
    
    q2="select * from paciente where id={}".format(a[1])
    b=list(database.query(q2))
    if len(b)>=1:
        b=b[0]
    else:
        b=[]
    
    q3="select * from auxenfermedades where id={}".format(session['historia'])
    
    c=[]
    r=list(database.query(q3))

    if len(r)>0:
        for k,l in r:
            c.append(l)
   
    q4="select recomendaciones,comidasrequeridas,evitarrequeridas from dieta where id={}".format(a[0])
    
    d=list(database.query(q4))
    if len(d)>=1:
        d=d[0]
    else:
        d=[]
    if len(d)>0:
        re="select comidas from requerida where comidasrequeridas={}".format(d[0])
        re=database.query(re)
        ev="select comidas from evitar where comidasrequeridas={}".format(d[0])
        ev=database.query(ev)
    q5="select * from resultados where id={}".format(a[0])

    
    e=list(database.query(q5))
    if len(e)>=1:
        e=e[0]
    else:
        e=[]
    q6="select * from resultados where id={}".format(a[0])

    return render_template("historia.html",a=zip(lista1,a),b=b,c=c,d=zip(["dieta"],d),e=zip(e,lista2),re=re,ev=ev)

@app.route('/preguntas',methods=['GET', 'POST'])

def preguntas():
    
    if request.method == 'POST':
        pregunta=request.form.get("pregunta")
        respuesta=request.form.get("respuesta")
        if request.form.get("nueva"):
            P.append((pregunta,respuesta))
        if request.form.get("volver"):
            session['preguntas']=list(P)
            return redirect(url_for('newhist'))
    return render_template("preguntas.html")