# 2016-07-07 Hypertension CDSS Eunsol Lee
# 
# 함수들이 먼저 나온 다음 뒤쪽에 main module이 있습니다.
# def로 시작하는 부분은 모두 함수입니다. 




# printString으로 문자열을 받아 출력한 후 입력을 그대로 넘겨주는 simple한 함수
def PrintAndInput (printString):
	print (printString)
	return input()

# Patient_GeneralInformatinon Table을 loading하는 함수
# database의 Patient_GeneralInformation Table에서 PatientID에 해당하는 환자가 있는지 검색

def LoadPatientInformation (cursor, patientID):
	
	# database에서 쿼리를 통해 Patient_ID열에 patientID와 일치하는 데이터베이스를 찾은 후 그 정보를 읽어옴

	cursor.execute ("SELECT * FROM Patient_GeneralInformation WHERE Patient_ID = %s;" % str(patientID))

	# 읽어온 데이터베이스를 patientGeneralInformation에 저장
	patientInformation = cursor.fetchone()

	# 만약 읽어온 정보가 아무것도 없다면 None을 반납
	# 그렇지 않다면 그 환자 정보를 돌려줌.
	if patientInformation == None:
		return False
	else:
		return patientInformation


# Patient_GeneralInformatinon Table을 만드는 함수
# 환자 입력 정보를 입력 받은 후, insert into (SQL 명령)을 통하여 database에 환자 정보를 추가한다.

def MakeNewPatient (cursor, patientID):

	patientName = PrintAndInput("환자 이름은?")
	patientSex = PrintAndInput("환자 성별은? (M/F)").upper()	#대분자로 만들어줌.
	patientBirthDate = PrintAndInput("환자 생일은? (YYYY-MM-DD 형식으로..)")

	# INSERT INTO로 데이터 베이스에 삽입.
	cursor.execute ('''INSERT INTO Patient_GeneralInformation (Patient_ID, KoreanName, Sex, BirthDate) 
		VALUES (%s, "%s", "%s", "%s");'''
		% (str(patientID), patientName, patientSex, patientBirthDate))

	# 삽입환 환자 정보를 LoadPatientInformation 함수를 이용해 다시 불러온 다음 그대로 반환.
	return LoadPatientInformation (cursor, patientID)  


# Patient_Disease Table을 loading하는 함수
# 환자 정보를 입력하고 수정하는 루틴
# 우선 추가 명령만..
# 
def ModifyPatientInformation (cursor, patientID):
	while True:
		command = int(PrintAndInput ("0: 나가기, 1: 질환 추가, 2: 복용 약 추가"))
		if command == 0: 
			break
		if command == 1:

			# 데이터베이스의 모든 질환을 불러온 다음 그대로 출력
			# 오류 체크 루틴은 귀찮으니 안만듬.
			print (LoadAllDisease (cursor)) 
			
			# 질환 ID를 입력받음. 
			diseaseID = PrintAndInput ("위 질환 중 추가할 질환의 ID를 선택해주세요.")
			
			# Patient_Disease 데이터베이스에 추가 Patient_ID랑 Disease_ID만 매치
			cursor.execute ('''INSERT INTO Patient_Disease (Patient_ID, Disease_ID) 
				VALUES (%s, %s);'''
				% (str(patientID), diseaseID))
			print ("%d 환자에게 %d 질환을 (아마) 성공적으로 추가했습니다." % (patientID, int(diseaseID)))

		if command == 2:

			# 위와 비슷하게 복용 약을 추가함.
			# 줄이 많기 때문에 for로 분리해서 출력
			# 입력은 drugID와 score만 입력 받음. 나머지는 나중에.......

			for row in LoadAllDrug (cursor):
				print (row)

			drugID = PrintAndInput ("위의 약물 중 추가할 약물의 ID를 선택해주세요.")
			score = PrintAndInput ("위의 약물에 대한 점수를 추가해주세요. (1은 기본 점수, < 1: 이 약은 별로임 > 1: 이 약은 좋음)")

			# Patient_Drug 데이터베이스에 추가 Patient_ID랑 Drug_ID, score만 입력


			for row in LoadAllDrug (cursor):
				if int(row[0]) == int(drugID):
					drugType = row[2]

			if 'drugType' in locals():
				cursor.execute ('''INSERT INTO Patient_Drug (Patient_ID, Drug_ID, Drug_Type, score) 
					VALUES (%s, %s, %s, %s);'''
					% (str(patientID), drugID, drugType, score))
				print ("%d 환자에게 %d 약물을 (아마) 성공적으로 추가했습니다." % ( patientID, int(drugID)))
			else:
				print ("약물 추가에 실패하였습니다.")
# 

# 모든 질환을 불러오는 함수

def LoadAllDisease (cursor):

	#쿼리로 Disease_List에 있는 모든 함수를 불러옴.
	#우선 ID랑 이름만 불러옵니다.
	cursor.execute ("SELECT Disease_ID, KoreanName, AdditionalName FROM Disease_LIST ORDER BY Disease_ID;")

	#모든 값을 반환
	return cursor.fetchall()

# 모든 약물을 불러오는 함수

def LoadAllDrug (cursor):

	# 쿼리로 Drug_GeneralInformation에 있는 모든 약물을 불러옴. 
	cursor.execute ("SELECT Drug_ID, KoreanBrandName, DrugType, Description FROM Drug_GeneralInformation;")

	return cursor


# 추천 약물을 구함.

def GetRecommendDrug (cursor, patientID):
	print ("")
	print ("%d 환자의 추천 약물을 구합니다." % patientID)

	# 모든 약물을 불러오고, 각 약물의 점수에 우선 1점을 부여한다.

	allDrug = LoadAllDrug(cursor).fetchall()
	drugScore = [1.0] * len(allDrug)
	drugExplanation = [[] for _ in range(len(allDrug))]

	# 쿼리로 Patient_Disease와 Patient_Drug에서 이 환자에 해당하는 정보를 모두 읽어온다.

	# 우선 Patient_Disease 목록을 뽑는다.
	cursor.execute ("SELECT Disease_ID FROM Patient_Disease WHERE Patient_ID = %d;" % patientID)
	patientDiseaseList = cursor.fetchall ()

	# 환자가 가지고 있는 모든 질환에 대해 연관이 있는 약물이 있는지 검사를 하기 위해 for 문을 돈다.
	print ("")
	print ("환자가 가지고 있는 질환 번호")
	for diseaseID in patientDiseaseList:
		
		print (diseaseID)
		# Drug_AllEffect 목록을 뽑은 후 해당하는 disease의 약물에 점수를 곱한다.
		allDrugEffect = cursor.execute ("SELECT * FROM Drug_AllEffect WHERE Disease = %d;" % diseaseID).fetchall()
		# 뽑힌 disease에 대해 해당하는 Drug_General이나 Drug_Type에 대해 모두 점수를 곱한다.
		
		count = 0
		for drug in allDrug:	#drug[0] : Drug_ID, drug[2]: DrugType
			for drugEffect in allDrugEffect:

				#만약 Drug_ID가 일치하거나 Drug_Type이 일치한다면..

				if drugEffect[1] and drugEffect[1] == drug[0] or drugEffect[2] and drugEffect[2] == drug[2]:
					
					drugScore[count] = drugScore[count] * drugEffect[6] # 해당하는 점수를 곱해줌.
					drugExplanation[count].append(["질환에 따른 Indication or CI", drugEffect])  # 귀찮으니까 
				
			count = count + 1	#drug 하나씩 넘어가므로..


	# 환자의 약물 경험을 읽고 그게 대한 고려

	print ("")
	print ("환자의 약물 정보")
	cursor.execute ("SELECT Drug_ID, Score, Drug_Type FROM Patient_Drug WHERE Patient_ID = %d;" % patientID)
	patientDrugList = cursor.fetchall ()
	for drugID, score, drugType in patientDrugList:

		print (drugID, score, drugType)
		count = 0

		for drug in allDrug:

			if drug[0] == drugID:
				drugScore[count] = drugScore[count] * score 		#개별 약물 점수를 곱한다
				drugExplanation[count].append(["환자 개인의 약물에 대한 평가", drugID, score])
		
			# 순수한 약물끼리의 상관관계에 대한 고려
	

			allDrugEffect = cursor.execute ("SELECT * FROM Drug_AllEffect WHERE OtherDrug_Type = %s AND Drug_Type = %s;" % (drugType, drug[2]))
			for drugEffect in allDrugEffect:

				drugScore[count] = drugScore[count] * drugEffect[6] # 해당하는 점수를 곱해줌.
				drugExplanation[count].append(["약물 상호작용에 따른 평가", drugEffect])  # 귀찮으니까 

			count = count + 1



	print ("")
	for i in range(len(drugScore)):
		print ("")
		print ('%s번 약물 %s는 %s 계열이며 %f 점수를 받았음.' % (allDrug[i][0], allDrug[i][1], allDrug[i][2], drugScore[i]))
		if drugExplanation[i]:
			print ('점수를 받은 특별한 이유 : ')
			print (drugExplanation[i])

	print ("")



# BP를 입력하는 루틴.

def ModifyPatientBP (cursor, patientID):
	
	SBP = PrintAndInput ("Systolic BP는?")
	DBP = PrintAndInput ("Diastolic BP는?")
	date = PrintAndInput ("측정 날짜는? (YYYY-MM-DD 형식으로..)")

	cursor.execute ('''INSERT INTO Patient_BP (Patient_ID, SBP, DBP, MeasuringDate)
		VALUES (%s, %s, %s, "%s");'''
		% (str(patientID), SBP, DBP, date))
	print ("%d 환자에게 혈압을 추가하였습니다." % (patientID))

# Database connection
# sqlite3로 만든 db와 연결하는 부분입니다. 

import sqlite3

con = sqlite3.connect("Hypertension_CDSS.db")
cursor = con.cursor()

# Python 2.x와 호환성을 위해...
# Python 2.x의 raw_input을 input에 overwrite, 따라서, 이 문장 아래에서는 input이 raw_input과 같은 역할을 함.
# Python 3.x에서는 아래의 구문이 에러를 발생시키는데, 따라서 except로 넘어가게 되고 그대로 진행하게 됨.
try:
	input = raw_input
except NameError:
        pass


# 데이터베이스로부터 환자 정보를 읽어옴.
# cursor: 데이터베이스의 cursor. 접근 단위
# patiendID: 환자 번호


# 메인 모듈

while True:

	# 어떤 동작을 할지 PrintAndInput이라는 함수를 통해서 물어보고 결과를 command에 저장

	command = int(PrintAndInput("0: 종료, 1: 환자(신규) 선택하기, 2: 환자 정보 입력 (질환, 약물), 3: 혈압 입력, 4: 약물 추천하기"))

	# 0을 입력시 while을 빠져나감으로서 프로그램 종료
	if command == 0:
		break

	# 1을 입력시 환자 선택 루틴으로
	if command == 1:		

		# patientID에 환자의 ID를 입력받음.
		patientID = int(PrintAndInput("환자의 ID는? (또는 신규 ID)"))

		# 미리 만들어둔 LoadPatientInformation이라는 함수를 통해 database를 통해 환자 정보를 읽어드림.
		# 환자 정보를 읽는데 성공을 하면 True를 반환.
		# 실패시 False를 반영하므로 else: 로 넘어간 후 새로운 환자에 대한 정보를 읽어들인다.

		patientInformation = LoadPatientInformation(cursor, patientID)
		if not patientInformation:
			command_sub = PrintAndInput(str(patientID) + " 환자 정보를 읽을 수 없습니다. 새로 만드시겠습니까? (y/?)")

			# y를 입력했을 때만 MakeNewPatient함수를 통해 새로운 환자를 생성한다.
			if command_sub == "y":
				patientInformation = MakeNewPatient(cursor, patientID)
				print (patientInformation)
				print ("위 환자 정보를 새로 만드는데 성공하였습니다.")
		else:
			print (patientInformation)
			print ("위 환자 정보를 읽어오는데 성공하였습니다.")

	# 2를 입력시 환자 정보 입력 루틴으로.
	if command >= 2 and command <= 4:

		# PatientInformation이 입렵된 적이 있는지 체크.

		if not 'patientInformation' in locals():
			print ("환자를 먼저 선택해주세요.")
		else:
			if command == 2: ModifyPatientInformation (cursor, patientID)
			if command == 3: ModifyPatientBP (cursor, patientID)
			if command == 4: 
				GetRecommendDrug (cursor, patientID)


# Database 닫기			
con.commit()
con.close()
