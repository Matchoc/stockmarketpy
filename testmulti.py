import multiprocessing

def test(x):
	print("processing " + str(x))
	for i in range(10000):
		x = x + x
	return x

if __name__ == '__main__':
	NUM_PROC = 20
	
	print("bleh")
	values = [x for x in range(2000000)]
	print("jamaisici")
	
	p = multiprocessing.Pool(NUM_PROC)
	r = p.map(test, values)
	print(r)