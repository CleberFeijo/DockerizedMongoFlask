import os
import pymongo
from flask import Flask, jsonify
from flask_pymongo import PyMongo
import pdfplumber

app = Flask(__name__)




#a função get_db conecta o app.py do flask com o mongodb, utilizando dos dados que foram criados no Dockerfile.

def get_db():
	app.config["MONGO_URI"] = 'mongodb://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] + '@' + os.environ['MONGODB_HOSTNAME'] + ':27017/' + os.environ['MONGODB_DATABASE']

	mongo = PyMongo(app)
	db = mongo.db

	return db





#a classe "inteiro_romano" serve para passar numeros inteiros para numeros romanos, eu a utilizo para poder utilizar um "contador"
#para ir passando pelos Títulos, Capítulos e Seções.

class inteiro_romano:
	def int_to_roman(self, input):
		ints = (1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1)				#Esta Função dentro da classe serve para pegar o valor de input
		nums = ('M', 'CM', 'D', 'CD','C', 'XC','L','XL','X','IX','V','IV','I')		#e transformá-lo em número romano.
		result = []																	#Seu resultado, armazenado na lista result
		for i in range(len(ints)):													#é retornado como ''.join pois é utilizado para completar
			count = int(input / ints[i])											#strings com o número romano equivalente ao número inteiro enviado
			result.append(nums[i] * count)
			input -= ints[i] * count
		return ''.join(result)




#a classe "ler_pdf", como o nome já diz, foi feita para fazer a leitura do pdf da constituição brasileira, utilizando o pdfplumber para tal.

class ler_pdf:
	def __init__(self):
		self.palavras = []
		self.linhas = []

	def leitor_de_pdf(self):
		pdf =  pdfplumber.open("constituicao_brasileira_1998.pdf")	#Esta Função dentro da classe "ler_pdf" utiliza o pdfplumber para abrir o pdf
		n = len(pdf.pages)											#salva na variável n o tamanho do pdf, e depois,
																	#em um for que passa por todas as páginas ele salva elas na lista palavras,
		for i in range(n):											#após separar as páginas por linhas,tanto pra excluir as strings do rodapé das páginas
			page = pdf.pages[i].extract_text()						#quanto pra facilitar a futura separação por blocos.
			if page != None:
				self.linhas = page.split("\n")
				remove_rodape = self.linhas[:-2]
				for j in range(0, len(remove_rodape)):
					self.palavras.append(remove_rodape[j])
		return self.palavras




#a classe "remove_pre_titulo" foi feita para remover todas as páginas anteriores ao Título I.

class remove_pre_titulo:
	def __init__(self):
		self.removido = []

	def remover_pre_titulo(self, palavras):
		if 'TÍTULO I –  ' in palavras:						#Esta Função dentro da classe "remove_pre_titulo" busca na lista palavras
			try:											#que tem todo o pdf separado por linhas a linha "Título I -  ",
				indice = palavras.index('TÍTULO I –  ')		#onde após encontrá-la, armazena o seu indice
			except ValueError:								#e o utiliza para apagar tudo que vem antes do Título I.
				indice = None
			self.removido = palavras[indice:]
		return self.removido




#a classe "passa_db" foi feita para fazer a inserção do artigo no banco de dados, como o nome já diz, ele passa para a data base.

class passa_db:
	def __init__(self):
		self.id_key = 0

	def PegaArtigo(self, resultado, artigo):
		db = get_db()								#Esta Função dentro da classe "passa_db" inicia a conexão com o mongodb,
		b = resultado.split('Art. ')[1:]			#utilizando a função "get_db", separa o bloco enviado por artigos
		c = []										#(pode ser um bloco de título(caso não tenha capítulos), um bloco de capítulo(caso não tenha seção)
		for u in b:									#ou um bloco de seção), armazena esses artigos em uma lista "c",
			c.append(u)								#passa por toda lista armazenando artigo por artigo no dict "artigo"
		c = ['Art. ' + u for u in c]				#(o qual já tem os campos título, capítulo e seção preenchidos)
		for count, value in enumerate(c):			#e lança os artigos um por um no banco de dados,
			artigo['teor'] = value					#utilizando também um contador "id_key" para chave id
			artigo['_id'] = self.id_key
			db.flaskdb.insert_one(artigo)
			self.id_key += 1




#a classe "separar_titulo" é a primeira classe do esquema de blocos, 
#ela separa o texto em blocos indo do Título I ao Título II, do II ao III e assim sucessivamente.

class separar_titulo:
	def __init__(self):
		self.bloco = []
		self.prox = 0
		self.atual = 0
		self.ind = 0
		self.define = ''

	def separar_bloco(self, palavras, artigo, y, i_r):
		try:
			self.prox = palavras.index('TÍTULO ' + i_r.int_to_roman(y+1) + ' –  ')		#Esta Função dentro da classe "separar_titulo"
		except ValueError:																#vai pegar o indice do próximo título
			self.prox = 135																#(se o indice for inexistente ele assume que chegamos no Título IX
			self.bloco = ' '.join(palavras[:self.prox])									#e utiliza o indice 135 que vai pegar até o fim do título IX)
		self.define = palavras[0]+palavras[1]											#ele armazena o título atual no dict artigo e cria o bloco_titulo.
		artigo['titulo'] = self.define
		self.bloco = ' '.join(palavras[:self.prox])
		return self.bloco




#a classe "separar_capitulo" separa o bloco gerado pela "separar_titulo" em blocos de capítulos. (apenas executa se for necessário)

class separar_capitulo:
	def __init__(self):
		self.bloco = []
		self.prox = 0
		self.atual = 0
		self.ind = 0
		self.define = ''

	def separar_bloco(self, palavras, bloco_titulo, artigo, x, i_r):
		try:
			self.prox = bloco_titulo.index('CAPÍTULO ' + i_r.int_to_roman(x+1))			#Esta Função dentro da classe "separar_capitulo"
		except ValueError:																#vai pegar o indice do próximo capitulo
			self.prox = None															#(se o indice for inexistente ele assume que chegamos
		self.atual = palavras.index('CAPÍTULO ' + i_r.int_to_roman(x) + ' –  ')			#ao final do bloco e define o indice do próximo como None
		self.define = palavras[self.atual]+palavras[self.atual+1]						#para ir até o final do bloco), ele armazena
		artigo['capitulo'] = self.define												#o capítulo atual no dict artigo e cria o bloco_capítulo.
		self.ind = bloco_titulo.index('CAPÍTULO ' + i_r.int_to_roman(x))
		self.bloco = ''.join(bloco_titulo[self.ind:self.prox])
		return self.bloco




#a classe "separar_secao" separa o bloco gerado pela "separar_capitulo" em blocos de seções. (apenas executa se for necessário)

class separar_secao:
	def __init__(self):
		self.bloco = []
		self.prox = 0
		self.atual = 0
		self.ind = 0
		self.define = ''

	def separar_bloco(self, palavras, bloco_capitulo, artigo, z, i_r):
		try:
			self.prox = bloco_capitulo.index('SEÇÃO ' + i_r.int_to_roman(z+1))	#Esta Função dentro da classe "separar_secao" vai pegar
		except ValueError:														#o indice da próxima seção(se o indice for inexistente
			self.prox = None													#ele assume que chegamos ao final do bloco e define
		self.atual = palavras.index('SEÇÃO ' + i_r.int_to_roman(z) + ' –  ')	#o indice da próxima como None para ir até o final do bloco)
		self.define = palavras[self.atual]+palavras[self.atual+1]				#ele armazena a seção atual no dict artigo e cria o bloco_seção.
		artigo['secao'] = self.define
		self.ind = bloco_capitulo.index('SEÇÃO ' + i_r.int_to_roman(z))
		self.bloco = ''.join(bloco_capitulo[self.ind:self.prox])
		return self.bloco




#a classe "extrair_artigos" vai gerar o dicionário "artigo", utilizar das classes anteriores para separar o texto em blocos,
#extrair todos os artigos um a um e os enviar para a "passa_db" para que sejam inseridos no banco de dados.

class extrair_artigos:
	def __init__(self):
		self.artigo = {'_id': [], 'titulo':[], 'capitulo':[], 'secao':[], 'teor':[]}
		self.y = 1
		self.x = 1
		self.z = 1

	def extrator(self, palavras, i_r, datab):
		while True:
			try:
				if 'TÍTULO ' + i_r.int_to_roman(self.y) + ' –  ' in palavras:			#Utiliza a Função "int_to_roman" para gerar os títulos
					bt = separar_titulo()												#com um contador, e procurá-lo em palavras		
					bloco_titulo = bt.separar_bloco(palavras, self.artigo, self.y, i_r)	#Cria o bloco_titulo utilizando a classe "separar_titulo" e sua função
					self.y += 1															#Soma 1 no parâmetro y que indica qual título estamos utilizando			
					self.x = 1															#Insere 1 no valor de x para resetar o parâmetro do capítulo

					if 'CAPÍTULO' in bloco_titulo:																#Utiliza a Função "int_to_roman" para gerar	
						while 'CAPÍTULO ' + i_r.int_to_roman(self.x) in bloco_titulo:							#os capítulos com um contador, e procurá-lo	
							bc = separar_capitulo()																#no bloco_título. Cria o bloco_capítulo
							bloco_capitulo = bc.separar_bloco(palavras, bloco_titulo, self.artigo, self.x, i_r)	#utilizando a classe "separar_capítulo" e sua função
							self.x += 1																			#Soma 1 no parâmetro x que indica qual capítulo estamos utilizando
							self.z = 1																			#Insere 1 no valor de z para resetar o parâmetro da seção

							if 'SEÇÃO' in bloco_capitulo:																#Utiliza a Função "int_to_roman" para gerar
								while 'SEÇÃO ' + i_r.int_to_roman(self.z) in bloco_capitulo:							#as seções com um contador, e procurá-la
									bs = separar_secao()																#no bloco_capítulo. Cria o bloco_seção
									bloco_secao = bs.separar_bloco(palavras, bloco_capitulo, self.artigo, self.z, i_r)	#utilizando a classe "separar_secao" e sua função
									self.z += 1																			#Soma 1 no parâmetro z que indica qual seção estamos utilizando

									datab.PegaArtigo(bloco_secao, self.artigo)		#Entra na função "PegaArtigo" para inserir o artigo no banco de dados
							else:
								self.artigo['secao'] = None						#Caso não tenha seção, insere Null no dicionário
								datab.PegaArtigo(bloco_capitulo, self.artigo)	#Entra na função "PegaArtigo" para inserir o artigo no banco de dados
					else:
						self.artigo['capitulo'] = None				#Caso não tenha capítulo, insere Null no dicionário
						self.artigo['secao'] = None					#Caso não tenha seção, insere Null no dicionário
						datab.PegaArtigo(bloco_titulo, self.artigo)	#Entra na função "PegaArtigo" para inserir o artigo no banco de dados

					try:
						indice = palavras.index('TÍTULO ' + i_r.int_to_roman(self.y) + ' –  ') 	#Utiliza a Função "int_to_roman" para gerar 
					except ValueError:															#o próximo título e deletar tudo que havia antes desse título
						indice = None															#(pois já foi utilizado), lembrando que y foi somado +1
					palavras = palavras[indice:]												#anteriormente, por isso que é o próximo título.

				else:							#Quando não houver mais Títulos na lista palavras, entramos no else e damos break
					break
			except ValueError:
				break




#na rota /extrair, sua função "extrair" é utilizada para iniciar o processo de extração de artigos do pdf e inserção dos mesmos no banco de dados.

@app.route('/extrair')
def extrair():

	i_r = inteiro_romano()
	p = ler_pdf()
	palavras = p.leitor_de_pdf()
	att = remove_pre_titulo()
	palavras_atualizado = att.remover_pre_titulo(palavras)
	datab = passa_db()
	extract = extrair_artigos()
	try:
		extract.extrator(palavras_atualizado, i_r, datab)
	except pymongo.errors.DuplicateKeyError:
		return jsonify(message='Os artigos já foram extraidos e salvos no banco de dados anteriormente!'), 201

	return jsonify(status=True,message='Artigos Extraidos com sucesso!'), 201




#na rota /, sua função "index" é a padrão que gera uma mensagem dizendo quais rotas a pessoa deve inserir
#para "extrair artigos" ou "acessar os artigos no banco de dados".

@app.route('/')
def index():
	return jsonify(
		status=True,
		message='Bem-Vindo ao Banco de Dados de Artigos da Constituição Brasileira de 1988. Utilize "localhost/extrair" para criar o banco de dados e extrair os artigos para ele. Utilize também "localhost/artigos" para acessar o banco de dados e os artigos.'
	)




#na rota /artigos, sua função "get_artigos" é utilizada para acessar os artigos no banco de dados para fácil acesso.

@app.route('/artigos', methods=['GET'])
def get_artigos():
	db = get_db()
	artigos = db.flaskdb.find()
	item = {}
	output = []
	for artigo in artigos:
		item = {'titulo': artigo['titulo'], 'capitulo': artigo['capitulo'], 'secao': artigo['secao'], 'teor': artigo['teor']}
		output.append(item)

	return jsonify({"Artigos Extraidos": output})




if __name__== '__main__':
	ENVIRONMENT_DEBUG = os.environ.get("APP_DEBUG", True)
	ENVIRONMENT_PORT = os.environ.get("APP_PORT", 5000)
	app.run(host='0.0.0.0', port=ENVIRONMENT_PORT, debug=ENVIRONMENT_DEBUG)
