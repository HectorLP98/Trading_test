from sklearn.model_selection import GridSearchCV
from sklearn.metrics import confusion_matrix, accuracy_score, average_precision_score, roc_auc_score, f1_score
from tabulate import tabulate


def get_scores_clasification(y_true, y_pred, table_name=''):
    """ 
    (Function)
        Esta funcion imprime una tabla con los 4 principales scores de clasification, estos son: [accuracy_score,
        average_precision_score, roc_auc_score, f1_score]
    (Parameters)
        y_true: Variable y verdadera
        y_pred: Varable y predicha
        table_name: [str] En caso de ser ingresada imprime como titulo el table_name
    """
    if table_name != '':
        table_name = " "+table_name+" "
        print(table_name.center(60,"*"))
    table = []
    table.append(["Accuracy",accuracy_score(y_true,y_pred), "-> 1"])
    table.append(["Average precision", average_precision_score(y_true, y_pred), "-> 1"])
    table.append(["Roc Auc", roc_auc_score(y_true, y_pred), "-> 1"])
    table.append(["F1", f1_score(y_true, y_pred), " -> 1"])
    
    headers = ["Score Fn", "Value","Ideal"]
    table_str = tabulate(table, headers, tablefmt='grid')

    print(table_str)



def grid_search(X, y,model, param_grid, cv=5, verbose=1, scoring='accuracy',return_train_score=False,
                show_params=False):
    """ 
    (Function)
        Esta funcion entrena un GridSearchCV para obtener los mejores hiper-parametros
    (Parameters)
        - X: Valores que seran X en el modelo
        - y: Valor de y, debe ser una variable
        - model: Modelo que se desea perfeccionar
        - param_grid: [dict] Con los hiperparametros a considerar
        - cv: Cantidad de folders para el CrossValidation, alternativamente puede usar TimeSeriesSplit
        - verbose: [int] Que tanta informacion se despliega default 1 (casi nada)
        - scoring: [str] Vea la tabla de scoring que se pueden usar, default accuracy
        - return_train_score: [bool] determina si calcula el score del train, afecta al performance default False
        - show_params: [bool] En caso de ser True imprime los mejores hiperpararametros y el score alcanzado
        - 
    """
    
    grid_search = GridSearchCV(estimator=model, param_grid=param_grid,
                               scoring=scoring, return_train_score=return_train_score,
                               cv=cv, n_jobs=-1, verbose=verbose)
    
    # Ajustar el modelo
    grid_search.fit(X, y)
    if show_params:
        # Imprimir los mejores parámetros y el mejor puntaje
        print("Mejores parámetros:", grid_search.best_params_)
        print("Mejor puntaje:", grid_search.best_score_)
    return grid_search