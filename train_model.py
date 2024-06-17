import os
import pickle
from skimage.io import imread
from skimage.transform import resize
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

# Prepare the data/images
image_directory = "./PetImages"
categories = ['Cat', 'Dog', 'Other']
data = []
labels = []

for category_idx, category in enumerate(categories):
    for file in os.listdir(os.path.join(image_directory, category)):
        img_path = os.path.join(image_directory, category, file)
        try:
            img = imread(img_path)
            img = resize(img, (20, 20))
            flattened_img = img.flatten()
            data.append(flattened_img)
            labels.append(category_idx)
        except Exception as e:
            print(f"Error reading image {img_path}: {e}")
            print("reading next image")
            continue  

data = np.asarray(data)
labels = np.asarray(labels)

# Split the data
x_train, x_test, y_train, y_test = train_test_split(data, labels, test_size=0.2,
                                                    shuffle=True, stratify=labels)

# Train the classifier
classifier = SVC()
parameters = [{'gamma': [0.01, 0.001, 0.0001], 'C': [1, 10, 100, 1000]}]
grid_search = GridSearchCV(classifier, parameters)
grid_search.fit(x_train, y_train)

# Test the model's performance
best_estimator = grid_search.best_estimator_
y_prediction = best_estimator.predict(x_test)
score = accuracy_score(y_prediction, y_test)
print('{}% of samples were correctly classified'.format(str(score * 100)))
pickle.dump(best_estimator, open('./model.p', 'wb'))