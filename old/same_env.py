import pandas as pd

class Checker:
    
    def __init__(self, file1, file2):
        self.f1 = file1
        self.f2 = file2
    
    def _find_unique(self):
        dim1 = self.f1.shape[0]
        dim2 = self.f2.shape[0]
        unicity = []
        package = []
        for i in range(dim1):
            unicity.append(self.f1.loc[i, 0])
            package.append(self.f1.loc[i, 0].split('==')[0])
        for j in range(dim2):
            if self.f2.loc[j, 0].split('==')[0] not in package:
                unicity.append(self.f2.loc[j, 0])
        return unicity
    
    def _convert(self, list):
        with open('requirements.txt', 'w+') as f:
            for items in list:
                f.write('%s\n' %items)
        f.close()
        
if __name__ == "__main__":
    df1 = pd.read_csv("requirements_airflow_env.txt", header=None)
    df2 = pd.read_csv("requirements_my_env.txt", header=None)
    checker = Checker(df1, df2)
    l = checker._find_unique()
    checker._convert(l)
    