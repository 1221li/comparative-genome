# -*- coding: utf-8 -*-
#!/usr/bin/env python3
'''
Created on Tue Dec 18 11:13:06 CST 2018
@Mail: minnglee@163.com
@Author: Ming Li
'''

import sys,os,logging,click,re

logging.basicConfig(filename=os.path.basename(__file__).replace('.py','.log'),
                    format='%(asctime)s: %(name)s: %(levelname)s: %(message)s',level=logging.DEBUG,filemode='w')
logging.info(f"The command line is:\n\tpython3 {' '.join(sys.argv)}")

def LoadMAFFileList(File):
    '''
    goat    AfricanBuffalo  /stor9000/apps/users/NWSUAF/2015060145/genomic_align/last_align/LastResultChr/1/AfricanBuffalo.1.final.maf
    goat    Argali  /stor9000/apps/users/NWSUAF/2015060145/genomic_align/last_align/LastResultChr/1/Argali.1.final.maf
    goat    BarbarySheep    /stor9000/apps/users/NWSUAF/2015060145/genomic_align/last_align/LastResultChr/1/BarbarySheep.1.final.maf
    '''
    List = []
    for line in File:
        line = line.strip().split()
        List.append(line[-1])
    return List
def GetErrorInfo(File):
    LogFile = open(File)
    for line in LogFile:
        if re.search('error|ERROR|Error|command not found', line):
            print(f'error in {File}')
            sys.exit()
    LogFile.close()
def ReName(maf,output):
    if len(str(maf)) > 5 : return maf.replace('.maf','')
    else : return f'{output}/{maf}'
def Submit(queue,corenum,memory,output,Name,Command):
    os.system(f'jsub -R "rusage[res=1]span[hosts=1]" \
                     -q {queue} \
                     -n {corenum} \
                     -M {memory*1000000} \
                     -o {output}/{Name}.o \
                     -e {output}/{Name}.e \
                     -J {Name}.MultiZ \
                     bash {Command}')
    '''
    os.system(f'touch {output}/{Name}.e')
    os.system(f'bash {Command}')
    '''
@click.command()
@click.option('-i','--input',type=click.File('r'),help='The input file',required=True)
#@click.option('-p','--path',type=str,help='MAF file path',default='./')
@click.option('-o','--output',type=str,help='The path of output file',default='multiz')
@click.option('-q','--queue',type=click.Choice(['cpu6130','jynodequeue','jyqueue','mem128queue','denovoqueue','normal','nodequeue']),help='The job queue',default='jynodequeue')
@click.option('-c','--corenum',type=int,help='The core number of job',default=8)
@click.option('-m','--memory',type=int,help='The memory of job (Gb)',default=40)
def main(input,output,queue,corenum,memory):
    if output[-1] == '/' : output = output[:-1]
    if not os.path.exists(output): os.system(f'mkdir -p {output}')
    MAFFileList = LoadMAFFileList(input)
#    print(MAFFileList) 
    NewList = list(MAFFileList)
    NewFileName = 1
    while len(MAFFileList) > 1 :
        for FileName in MAFFileList:
            if os.path.isfile(f'{output}/{FileName}.e'):
                GetErrorInfo(f'{output}/{FileName}.e')
                if FileName not in NewList: NewList.append(FileName)
        while len(NewList) >= 2:
            File1 = ReName(NewList[0],output)
            File2 = ReName(NewList[1],output)
            os.system(f'echo "multiz {File1}.maf {File2}.maf 0 all > {output}/{NewFileName}.maf" > {output}/{NewFileName}.sh')
            os.system(f'chmod 755 {output}/{NewFileName}.sh')
            Submit(queue,corenum,memory,output,NewFileName,f'{output}/{NewFileName}.sh')
            if os.path.exists(f'{File1}.e'): os.system(f'rm {File1}.e')
            if os.path.exists(f'{File2}.e'): os.system(f'rm {File2}.e')
#            print(NewList)
            MAFFileList.append(NewFileName)
            MAFFileList.remove(NewList.pop(0))
            MAFFileList.remove(NewList.pop(0))
            NewFileName += 1
if __name__ == '__main__':
    main()
