from sklearn import svm

if __name__ == '__main__':
	X = [[0, 0], [1, 1], [2,2]]
	y = [0, 1, 10]
	clf = svm.SVC()
	clf.fit(X, y)
	print(clf.predict([[5., 5.]]))