ch_mas = ["妈妈","爸爸","学习","学","学校"]
readystr = "".join(map(str, ch_mas))
filt_ch_mas = []


print(readystr)


for i in readystr:
    filt_ch_mas.append(i)

    
print(set(filt_ch_mas))