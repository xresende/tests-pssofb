para plotar os resultados do benchmarking (exemplo):

- cd /home/sirius/repos-dev/dev-packages/siriuspy/siriuspy/pwrsupply/tests
- git checkout master

```python3
import sofb2bsmp
datafile = '/home/sirius/repos-dev/tests-pssofb/2020-07-15/lnls561-linux-set-eth-pru-serial485-master-log.txt'
sofb2bsmp.plot_result_hist(datafile, title='set, (eth-with-log), histogram (5000)')
sofb2bsmp.plot_result_time(datafile, title='set, (eth-with-log), time (5000)')
sofb2bsmp.plot_result_perc(datafile, title='set, (eth-with-log), perc (5000)')
```
