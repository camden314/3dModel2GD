import __init__ as level
import msgport

test = level.Level("test")

b1 = test.addBlock(507,200,100)

level.Transformer(b1) \
	 .copyAll() \
	 .rotate(45) \
	 .addToLevel(test)

msgport.uploadToGD(test)