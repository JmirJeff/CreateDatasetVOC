import random

with open('vehicles/ImageSets/Main/trainval.txt', 'r') as f:
    lista = f.read().split('\n')
    cantTotal = len(lista)
    trainCount = int(cantTotal*0.7)
    valCount = int(cantTotal*0.15)
    testCount = cantTotal - trainCount - valCount
    train = random.sample(lista,trainCount)
    fTrain = open('vehicles/ImageSets/Main/train2.txt','w')
    fTrainval = open('vehicles/ImageSets/Main/trainval2.txt','w')
    for i in train:
        fTrain.write(i+'\n')
        fTrainval.write(i+'\n')
        lista.remove(i)
    val = random.sample(lista,valCount)
    fVal = open('vehicles/ImageSets/Main/val2.txt','w')
    for i in val:
        fVal.write(i+'\n')
        fTrainval.write(i+'\n')
        lista.remove(i)
    fTest = open('vehicles/ImageSets/Main/test2.txt','w')
    for i in lista:
        fTest.write(i+'\n')
    fTrain.close()
    fTrainval.close()
    fVal.close()
    fTest.close()
