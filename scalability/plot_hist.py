import matplotlib.pyplot as plt
import numpy as np
import pandas as pd 
import seaborn as sns

data = pd.read_csv('fct-50.log', delim_whitespace=True)
print(data.head())

# kernel_slice = data[data['Impl'] == 'kernel_plain']
# sns.distplot(kernel_slice['FctUs'])
# plt.savefig('kernel_plot_50.pdf')

ccp_slice = data[data['Impl'] == 'ccp_plain']
sns.distplot(ccp_slice['FctUs'])
plt.savefig('ccp_plot_50.pdf')