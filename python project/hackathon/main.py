from flask import Flask
from flask import Flask, render_template, request,redirect
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def epsilon_form():
    if request.method == 'POST':
        epsilon = float(request.form['epsilon'])
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        import seaborn as sns
        df = pd.read_csv('C:/Users/bhargav/Downloads/IDS_Data1.csv')
        df
        df.describe()

        df.info()
        dict1={}
        df.columns

        df.shape

        sns.countplot(x='class', data=df)

        from sklearn import preprocessing
        lab = preprocessing.LabelEncoder()

        df['service'] = lab.fit_transform(df['service'])
        df['flag'] = lab.fit_transform(df['flag'])
        df['protocol_type'] = lab.fit_transform(df['protocol_type'])
        df['class'] = lab.fit_transform(df['class'])

        df

        df['class'].value_counts()

        df.info()

        corr_matrix = df.corr()
        corr_matrix

        corr_matrix['class'].sort_values(ascending=False)

        # correlations = df.corr()['class'].abs().sort_values(ascending=False)
        # N = 5  # Set the number of features you want to select
        # top_features = correlations[1:N+1].index

        x = df.iloc[:, df.columns != 'class']
        y = df.iloc[:, df.columns == 'class']

        from sklearn.metrics import classification_report
        from sklearn import model_selection
        from sklearn.metrics import r2_score

        X_train, X_test, Y_train, Y_test = model_selection.train_test_split(x, y, test_size=0.2, random_state=0)

        from sklearn.ensemble import RandomForestClassifier

        rf_model = RandomForestClassifier(n_estimators=100)
        Y_train = np.ravel(Y_train)
        rf_model.fit(X_train, Y_train)

        y_pred = rf_model.predict(X_test)

        # Summary of the predictions made by the classifier

        print("Random Forest Algorithm")
        print(classification_report(Y_test, y_pred))

        # Accuracy Score
        from sklearn.metrics import accuracy_score
        print("Accuracy Score: ", accuracy_score(y_pred, Y_test))

        print("\n\nr2_score is ", r2_score(Y_test, y_pred))

        from sklearn import tree

        dt_model = tree.DecisionTreeClassifier()
        dt_model.fit(X_train, Y_train)

        y_pred = dt_model.predict(X_test)

        # Summary of the predictions made by the classifier

        print("Decision Tree Algorithm")
        print(classification_report(Y_test, y_pred))

        # Accuracy Score
        from sklearn.metrics import accuracy_score
        print("Accuracy Score: ", accuracy_score(y_pred, Y_test))

        print("\n\nr2_score is ", r2_score(Y_test, y_pred))

        def generate_adversarial_examples(X, epsilon):
            perturbation = np.random.uniform(-epsilon, epsilon, size=X.shape)
            adv_examples = X + perturbation
            return adv_examples

        # Generate adversarial examples for Random Forest Classifier
        adv_examples_rf = generate_adversarial_examples(X_test, epsilon)

        # Generate adversarial examples for Decision Tree Classifier
        adv_examples_dt = generate_adversarial_examples(X_test, epsilon)

        # Test the models on the generated adversarial examples
        y_pred_rf_adv = rf_model.predict(adv_examples_rf)
        y_pred_dt_adv = dt_model.predict(adv_examples_dt)

        # Evaluation on adversarial examples
        print("Random Forest - Accuracy Score on Adversarial Examples: ", accuracy_score(y_pred_rf_adv, Y_test))
        print("Decision Tree - Accuracy Score on Adversarial Examples: ", accuracy_score(y_pred_dt_adv, Y_test))
        dict1['acc_rf1']= accuracy_score(y_pred_rf_adv, Y_test)
        dict1['acc_dt1']= accuracy_score(y_pred_dt_adv, Y_test)
        from sklearn.model_selection import train_test_split

        # Split the dataset into train and test sets
        X_train, X_test, Y_train, Y_test = train_test_split(x, y, test_size=0.2, random_state=42)

        # Split the training data into genuine and adversarial portions
        X_train_genuine, X_train_adv, Y_train_genuine, Y_train_adv = train_test_split(X_train, Y_train, test_size=0.5,
                                                                                      random_state=42)

        # Generate adversarial examples on half of the training data
        adv_examples_train = generate_adversarial_examples(X_train_adv, epsilon)

        # Assuming Y_adversarial_train represents labels for adversarial examples
        Y_adversarial_train = np.ones(len(adv_examples_train)).reshape(-1, 1)

        # Combine genuine and adversarial examples with labels for training
        X_combined_train = np.concatenate((X_train_genuine, adv_examples_train))
        Y_combined_train = np.concatenate((Y_train_genuine, Y_adversarial_train))
        Y_combined_train = Y_combined_train.ravel()

        # Retrain the models with the combined genuine and adversarial training data
        rf_model.fit(X_combined_train, Y_combined_train)
        dt_model.fit(X_combined_train, Y_combined_train)

        # Evaluate models on the separate test dataset
        y_pred_rf_test = rf_model.predict(X_test)
        y_pred_dt_test = dt_model.predict(X_test)

        # Assess performance on the test dataset
        test_accuracy_rf = accuracy_score(y_pred_rf_test, Y_test)
        test_accuracy_dt = accuracy_score(y_pred_dt_test, Y_test)
        print("Random Forest - Accuracy on Test Data: ", test_accuracy_rf)
        print("Decision Tree - Accuracy on Test Data: ", test_accuracy_dt)

        adv_examples_test = generate_adversarial_examples(X_test, epsilon)

        # Assuming Y_adversarial_test represents labels for adversarial examples
        Y_adversarial_test = np.ones(len(adv_examples_test)).reshape(-1, 1)

        # Evaluate the models on the generated adversarial examples
        y_pred_rf_adv = rf_model.predict(adv_examples_test)
        y_pred_dt_adv = dt_model.predict(adv_examples_test)

        # Assess the accuracy on the adversarial examples
        accuracy_rf_adv = accuracy_score(y_pred_rf_adv, Y_adversarial_test)
        accuracy_dt_adv = accuracy_score(y_pred_dt_adv, Y_adversarial_test)

        print("Random Forest - Accuracy on Adversarial Examples: ", accuracy_rf_adv)
        print("Decision Tree - Accuracy on Adversarial Examples: ", accuracy_dt_adv)
        dict1['acc_rf2']=accuracy_rf_adv
        dict1['acc_dt2']=accuracy_dt_adv
        # Use the epsilon value in your code (e.g., generate adversarial examples)
        # You may want to process and store the value in your backend.
        return render_template('results.html', dict1=dict1, epsilon=epsilon)
    return render_template('form.html')


if __name__ == '__main__':
    app.run()