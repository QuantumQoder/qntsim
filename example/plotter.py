import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

"""
#Linear Topology
#15 Trials
Avg_Physical_Ent_Time=[0.004500350020000001, 0.007467040021333334, 0.013717273365333333, 0.013350408345999995, 0.017151201706000003, 0.016967541691999998, 0.020267238350666666, 0.01621751836866667, 0.024050723373999994, 0.025384126695333332, 0.024367786708666666, 0.02616751836399999]

Avg_Virtual_Ent_Time=[0.01276704001133333, 0.0, 0.0060003500100000015, 0.010050735009999997, 0.013967436679333332, 0.013900863349333329, 0.010117075022, 0.012367343352, 0.012933916694666666, 0.015684091695333337, 0.01413394002333334, 0.021150968371333335]

#30 Trials

Avg_Physical_Ent_Time= [0.00450035002, 0.007000350019999996, 0.01216722086433334, 0.012700355844666663, 0.018034535041, 0.017509249191666666, 0.015567150849333331, 0.02018430753833333, 0.02598417921133334, 0.026242570865999994, 0.022534395037666653, 0.024825828361666656]

Avg_Virtual_Ent_Time= [0.012617028343999996, 0.0, 0.007217063345999999, 0.011084150010999997, 0.014409138345333332, 0.014225857514666661, 0.012225519193999996, 0.01179230251633334, 0.01162550752633333, 0.014367355027666673, 0.02049251253366666, 0.020676003371000003]


#50 Trials
Avg_Physical_Ent_Time= [0.004500350019999995, 0.007420371021199995, 0.012230556531000008, 0.013485406012600008, 0.018326162039400008, 0.017165896025399998, 0.016470553018800002, 0.017335794532999996, 0.025675822543600024, 0.0240457665284, 0.022956095539199993, 0.02716093103180002]

Avg_Virtual_Ent_Time= [0.012760371011200004, 0.0, 0.006595374511399994, 0.011565836512199995, 0.012335693010600004, 0.01364085401500001, 0.010765437523599992, 0.012810651018599994, 0.010900455023599993, 0.014935735029799991, 0.01709573852819999, 0.023125983540200016]

x_axis=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
"""
#Extended Star
"""
Avg_Physical_Ent_Time =  [0.005500350019999996, 0.007740392022399994, 0.03366221212339991, 0.03624189004620001, 0.0351463615444001, 0.01568083302539999]

Avg_Virtual_Ent_Time =  [0.0051352835154, 0.0, 0.015845836541999992, 0.02996155406219999, 0.022895934548000017, 0.007770336015600003]

Avg_fidelity_physical =  [0.9350000000000004, 0.865, 2.4030000000000036, 2.2229999999999994, 2.0580000000000083, 0.6350000000000007]

Avg_fidelity_virtual =  [0.8009999999999998, 0.865, 2.4030000000000036, 2.034320000000002, 1.8894400000000033, 0.6350000000000007]
"""
"""
Avg_Physical_Ent_Time =  [0.005500350019999996, 0.007555381521799995, 0.010814049706799977, 0.01120225117973334, 0.012472162516733368, 0.014760784024199988]

Avg_Virtual_Ent_Time =  [0.005095255512799999, 0.0, 0.004721903512133332, 0.00918712401873333, 0.008247012016466675, 0.010065486522000004]

Avg_fidelity_physical =  [0.9350000000000004, 0.865, 0.8010000000000012, 0.7409999999999998, 0.6860000000000027, 0.6350000000000007]

Avg_fidelity_virtual =  [0.8009999999999998, 0.865, 0.8010000000000012, 0.6766933333333343, 0.6337333333333345, 0.6350000000000007]

x_axis = [1, 2, 3, 4, 5, 6]
"""
"""
Avg_Physical_Ent_Time =  [0.004500350019999995, 0.007140357020399994, 0.011250525030000008, 0.013585420013000005, 0.01827620403980001, 0.0156608925234, 0.017205518015999996, 0.015860773532199994, 0.02658582254260002, 0.024940805029400003, 0.024231134039799998, 0.02696587852940001]

Avg_Virtual_Ent_Time =  [0.012740371011200007, 0.0, 0.007525402513399993, 0.012075854012999997, 0.011790686009600006, 0.01330586451220001, 0.013345563527999996, 0.012870675518799994, 0.013290616028599997, 0.014780714028599998, 0.016495728027599993, 0.022236060539200006]

Avg_fidelity_physical =  [0.9350000000000004, 0.865, 0.8009999999999998, 0.7409999999999998, 0.686, 0.6350000000000007, 0.5880000000000002, 0.5440000000000004, 0.5040000000000002, 0.46600000000000014, 0.43099999999999994, 0.3990000000000006]

Avg_fidelity_virtual =  [0.8090399999999999, 0.865, 0.8009999999999998, 0.7409999999999998, 0.4704, 0.6350000000000007, 0.5880000000000002, 0.5440000000000004, 0.5040000000000002, 0.46600000000000014, 0.43099999999999994, 0.3990000000000006]

x_axis = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
"""
"""
Avg_Physical_Ent_Time =  [0.004500350019999995, 0.007540374521399995, 0.012590567031600006, 0.013495395512400008, 0.018131190040200012, 0.0173208995268, 0.017180535516999995, 0.016350808532599993, 0.025390808542200008, 0.022545770027599995, 0.023591095541199997, 0.02682585753040001]

Avg_Virtual_Ent_Time =  [0.004595360510199995, 0.0, 0.006930416512599996, 0.011225833011599995, 0.008920416513799994, 0.014000868015400009, 0.012340528527399997, 0.013710700019399997, 0.012880616029599995, 0.014245682527599992, 0.017020728029600002, 0.02016093103460002]

Avg_fidelity_physical =  [0.9350000000000004, 0.865, 0.8009999999999998, 0.7409999999999998, 0.686, 0.6350000000000007, 0.5880000000000002, 0.5440000000000004, 0.5040000000000002, 0.46600000000000014, 0.43099999999999994, 0.3990000000000006]

Avg_fidelity_virtual =  [0.9350000000000004, 0.865, 0.8009999999999998, 0.7409999999999998, 0.686, 0.6350000000000007, 0.5880000000000002, 0.5440000000000004, 0.5040000000000002, 0.46600000000000014, 0.43099999999999994, 0.3990000000000006]

x_axis = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
"""

"""
#Extended Star 50 Trials
Avg_Physical_Ent_Time =  [0.005500350019999996, 0.0071853605205999945, 0.011604087041666641, 0.011418929513533337, 0.011602111181200032, 0.015545836526399988]

Avg_Virtual_Ent_Time =  [0.0037952415127999973, 0.0, 0.004918584179333329, 0.008125444517000011, 0.009658864188533348, 0.008240371017200005]

Avg_fidelity_physical =  [0.9350000000000004, 0.865, 0.8010000000000012, 0.7409999999999998, 0.6860000000000027, 0.6350000000000007]

Avg_fidelity_virtual =  [0.9350000000000004, 0.865, 0.8010000000000012, 0.7409999999999998, 0.6860000000000027, 0.6350000000000007]

x_axis = [1, 2, 3, 4, 5, 6]
"""
"""
#Extended Star 100 Trials
Avg_Physical_Ent_Time =  [0.0055003500199999975, 0.007600385021699993, 0.0108923853737667, 0.011687282681300008, 0.01204880468229997, 0.015428324276100018]

Avg_Virtual_Ent_Time =  [0.0038727467632000056, 0.0, 0.00514193151343332, 0.008521291266766666, 0.01018806527306667, 0.009470427020500011]

Avg_fidelity_physical =  [0.9350000000000013, 0.8649999999999991, 0.8009999999999949, 0.7410000000000058, 0.6860000000000048, 0.6349999999999993]

Avg_fidelity_virtual =  [0.9350000000000013, 0.8649999999999991, 0.8009999999999949, 0.7410000000000058, 0.6860000000000048, 0.6349999999999993]

x_axis = [1, 2, 3, 4, 5, 6]
"""
"""
#Linear 100 Trials
Avg_Physical_Ent_Time =  [0.004500350019999991, 0.007340365770899991, 0.012720572281499986, 0.013242886762100028, 0.018913714542099985, 0.01675340477540004, 0.016270511016700028, 0.016205841784600022, 0.026298329543800035, 0.025000817279500032, 0.023778597289999998, 0.026243387280899984]

Avg_Virtual_Ent_Time =  [0.004525353509999991, 0.0, 0.007542907763499994, 0.012278361013099998, 0.009470442764100015, 0.014085866265000024, 0.012100500525899999, 0.012470637018199993, 0.012868065277399992, 0.016275759531699983, 0.01856329803039998, 0.01939841353460002]

Avg_fidelity_physical =  [0.9350000000000013, 0.8649999999999991, 0.8010000000000008, 0.7409999999999998, 0.6860000000000005, 0.6349999999999993, 0.5880000000000005, 0.543999999999999, 0.5039999999999994, 0.4660000000000006, 0.4309999999999995, 0.3990000000000007]

Avg_fidelity_virtual =  [0.9350000000000013, 0.8649999999999991, 0.8010000000000008, 0.7409999999999998, 0.6860000000000005, 0.6349999999999993, 0.5880000000000005, 0.543999999999999, 0.5039999999999994, 0.4660000000000006, 0.4309999999999995, 0.3990000000000007]

x_axis = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
"""
"""
Avg_Physical_Ent_Time =  [0.004500350019999995, 0.007420371021199994, 0.013660605531800008, 0.013430395512000008, 0.017916193540400013, 0.017845955527600002, 0.016240511017399997, 0.01603080153339999, 0.026340840043400024, 0.02398079802819999, 0.02366606403879999, 0.026850934533200026]

Avg_fidelity_physical =  [0.9350000000000004, 0.865, 0.8009999999999998, 0.7409999999999998, 0.686, 0.6350000000000007, 0.5880000000000002, 0.5440000000000004, 0.5040000000000002, 0.46600000000000014, 0.43099999999999994, 0.3990000000000006]

x_axis = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
"""
"""
#Extended star 500 iterations
Avg_Physical_Ent_Time_100 =  [0.007877900772599993, 0.011135730374100037, 0.011493934180366674, 0.011835456181733303, 0.015525833025900018]
Avg_Physical_Ent_Time_200 =  [0.007692890271999991, 0.011084061957299924, 0.011485601430483333, 0.012095056724150108, 0.015019555899900047]
Avg_Physical_Ent_Time_300 =  [0.007492878604766684, 0.01113100912411098, 0.011493379791544278, 0.012214367238266615, 0.015312497359066727]
Avg_Physical_Ent_Time_400 =  [0.007462251708875062, 0.011238237082666509, 0.011593106680691374, 0.012102555265708163, 0.015261448837800062]
Avg_Physical_Ent_Time_500 =  [0.007536380821640087, 0.011186734574173234, 0.011564604813959743, 0.012125807482479788, 0.015245324975460066]

Avg_Virtual_Ent_Time_100 =  [0.0, 0.0051285970131333194, 0.008095430516200009, 0.010037216189666671, 0.009967953271000012]
Avg_Virtual_Ent_Time_200 =  [0.0, 0.005102349055199979, 0.008391689558366623, 0.009938869439266581, 0.009182920019600017]
Avg_Virtual_Ent_Time_300 =  [0.0, 0.005207770097011125, 0.0083904421834777, 0.009845806883277627, 0.008967079685733358]
Avg_Virtual_Ent_Time_400 =  [0.0, 0.005183392909316755, 0.008256062954083241, 0.01001700129340816, 0.008672895518525025]
Avg_Virtual_Ent_Time_500 =  [0.0, 0.005160266013413466, 0.008232270499946574, 0.010115884722839813, 0.00859738781834]

Avg_fidelity_physical_100 =  [0.8649999999999991, 0.8009999999999949, 0.7410000000000058, 0.6860000000000048, 0.6349999999999993]
Avg_fidelity_physical_200 =  [0.8650000000000007, 0.8009999999999913, 0.7409999999999978, 0.6859999999999952, 0.6350000000000022]
Avg_fidelity_physical_300 =  [0.8650000000000034, 0.8010000000000066, 0.7409999999999937, 0.6859999999999994, 0.6349999999999985]
Avg_fidelity_physical_400 =  [0.8650000000000049, 0.801000000000016, 0.7409999999999916, 0.6860000000000084, 0.6349999999999966]
Avg_fidelity_physical_500 =  [0.8650000000000057, 0.801000000000005, 0.7409999999999904, 0.6860000000000132, 0.6349999999999955]

Avg_fidelity_virtual_100 =  [0.8649999999999991, 0.8009999999999949, 0.7410000000000058, 0.6860000000000048, 0.6349999999999993]
Avg_fidelity_virtual_200 =  [0.8650000000000007, 0.8009999999999913, 0.7409999999999978, 0.6859999999999952, 0.6350000000000022]
Avg_fidelity_virtual_300 =  [0.8650000000000034, 0.8010000000000066, 0.7409999999999937, 0.6859999999999994, 0.6349999999999985]
Avg_fidelity_virtual_400 =  [0.8650000000000049, 0.801000000000016, 0.7409999999999916, 0.6860000000000084, 0.6349999999999966]
Avg_fidelity_virtual_500 =  [0.8650000000000057, 0.801000000000005, 0.7409999999999904, 0.6860000000000132, 0.6349999999999955]

x_axis = [2, 3, 4, 5, 6]
"""

#Linear 500 iterations
Avg_Physical_Ent_Time_100 =  [0.007210360520599992, 0.012300560030799988, 0.01367540951290003, 0.018461172539999977, 0.016798375025100044, 0.016850514516100035, 0.016108282282400018, 0.028218417045900033, 0.023978250778100025, 0.0235385745392, 0.025635880280800008]
Avg_Physical_Ent_Time_200 =  [0.007310364895849991, 0.011895546030599946, 0.013706660387849979, 0.018449932165000044, 0.017035887275500063, 0.01705303814155, 0.01614828665775004, 0.027797145170299936, 0.024013276154000035, 0.023884848164999996, 0.026838411782049983]
Avg_Physical_Ent_Time_300 =  [0.007323699104233344, 0.012333894531066605, 0.013902924680133266, 0.018456183040166736, 0.016861720608533397, 0.016942205683433305, 0.016234955949566712, 0.027424203127999855, 0.024256625529366648, 0.024606132874933382, 0.02685841294839999]
Avg_Physical_Ent_Time_400 =  [0.0073128653333750585, 0.012440564843600009, 0.01390480113859991, 0.01859618829042508, 0.01704901446310006, 0.017143051267474962, 0.016177048470775054, 0.027291492607199857, 0.024338296279299954, 0.02446175379155002, 0.026455907406425075]
Avg_Physical_Ent_Time_500 =  [0.0073343664709400866, 0.012459565281240065, 0.013725416863239897, 0.018706197390760092, 0.017203899875740065, 0.01722055791802, 0.015995294533240056, 0.02720936734471985, 0.024264792779179926, 0.024169619691119963, 0.026723413181740138]

Avg_Virtual_Ent_Time_100 =  [0.0, 0.006557876261199993, 0.011613366261099996, 0.008780413013600013, 0.013815890762600022, 0.011482970774899997, 0.013355701769500001, 0.012908088028099996, 0.014270705279699982, 0.017238240278099982, 0.02041341178550002]
Avg_Virtual_Ent_Time_200 =  [0.0, 0.0066728762615000155, 0.011907109261999995, 0.008974170013949984, 0.013964631139450033, 0.012336761901449998, 0.01380446052019999, 0.012771824027549998, 0.014660707029350017, 0.01814203753019997, 0.020617195910800027]
Avg_Virtual_Ent_Time_300 =  [0.0, 0.006707877428233369, 0.012119207178866663, 0.008975421763899967, 0.013734207180633371, 0.012536361276833328, 0.013402356186466624, 0.013509783279100003, 0.01519156253026669, 0.01803995069673339, 0.020737636786333277]
Avg_Virtual_Ent_Time_400 =  [0.0, 0.0067510030117000006, 0.01194899301189999, 0.009281684451749957, 0.013768999138950043, 0.012423649589299996, 0.01324756189442503, 0.0132581015911, 0.01489009427949997, 0.017820771342025116, 0.02069845903594991]
Avg_Virtual_Ent_Time_500 =  [0.0, 0.006853380461939981, 0.011993870112039987, 0.009200929114119958, 0.013740876063800044, 0.012657538327240002, 0.013416196519580072, 0.013178598878580004, 0.01498821857927995, 0.017813771779620097, 0.02073946358629998]

Avg_fidelity_physical_100 =  [0.8649999999999991, 0.8010000000000008, 0.7409999999999998, 0.6860000000000005, 0.6349999999999993, 0.5880000000000005, 0.543999999999999, 0.5039999999999994, 0.4660000000000006, 0.4309999999999995, 0.3990000000000007]
Avg_fidelity_physical_200 =  [0.8650000000000007, 0.8009999999999985, 0.7410000000000017, 0.6860000000000038, 0.6350000000000022, 0.5879999999999975, 0.543999999999998, 0.5040000000000012, 0.4659999999999986, 0.43099999999999844, 0.39900000000000074]
Avg_fidelity_physical_300 =  [0.8650000000000034, 0.8009999999999949, 0.7410000000000058, 0.6860000000000048, 0.6349999999999985, 0.5879999999999963, 0.5440000000000007, 0.5040000000000002, 0.46599999999999825, 0.4309999999999982, 0.3990000000000008]
Avg_fidelity_physical_400 =  [0.8650000000000049, 0.8009999999999932, 0.7410000000000039, 0.6860000000000035, 0.6349999999999966, 0.5879999999999957, 0.5440000000000034, 0.5039999999999979, 0.46600000000000075, 0.4310000000000016, 0.39900000000000085]
Avg_fidelity_physical_500 =  [0.8650000000000057, 0.800999999999992, 0.7410000000000002, 0.6859999999999985, 0.6349999999999955, 0.587999999999999, 0.5440000000000031, 0.5039999999999965, 0.4660000000000022, 0.4310000000000036, 0.39900000000000085]

Avg_fidelity_virtual_100 =  [0.8649999999999991, 0.8010000000000008, 0.7409999999999998, 0.6860000000000005, 0.6349999999999993, 0.5880000000000005, 0.543999999999999, 0.5039999999999994, 0.4660000000000006, 0.4309999999999995, 0.3990000000000007]
Avg_fidelity_virtual_200 =  [0.8650000000000007, 0.8009999999999985, 0.7410000000000017, 0.6860000000000038, 0.6350000000000022, 0.5879999999999975, 0.543999999999998, 0.5040000000000012, 0.4659999999999986, 0.43099999999999844, 0.39900000000000074]
Avg_fidelity_virtual_300 =  [0.8650000000000034, 0.8009999999999949, 0.7410000000000058, 0.6860000000000048, 0.6349999999999985, 0.5879999999999963, 0.5440000000000007, 0.5040000000000002, 0.46599999999999825, 0.4309999999999982, 0.3990000000000008]
Avg_fidelity_virtual_400 =  [0.8650000000000049, 0.8009999999999932, 0.7410000000000039, 0.6860000000000035, 0.6349999999999966, 0.5879999999999957, 0.5440000000000034, 0.5039999999999979, 0.46600000000000075, 0.4310000000000016, 0.39900000000000085]
Avg_fidelity_virtual_500 =  [0.8650000000000057, 0.800999999999992, 0.7410000000000002, 0.6859999999999985, 0.6349999999999955, 0.587999999999999, 0.5440000000000031, 0.5039999999999965, 0.4660000000000022, 0.4310000000000036, 0.39900000000000085]

x_axis = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

#Entanglement Time vs Distance from source( hops from source)
#fig, ax = plt.subplots()
fig = plt.figure()
ax = fig.add_axes([0.1, 0.1, 0.70, 0.75])
ax.xaxis.set_major_locator(MaxNLocator(integer=True))

for i in range(5):
	ax.plot(x_axis, Avg_Physical_Ent_Time_100, marker='o' ,label = r'Phy 100 iter')
	ax.plot(x_axis, Avg_Physical_Ent_Time_200, marker='o' ,label = r'Phy 200 iter')
	ax.plot(x_axis, Avg_Physical_Ent_Time_300, marker='o' ,label = r'Phy 300 iter')
	ax.plot(x_axis, Avg_Physical_Ent_Time_400, marker='o' ,label = r'Phy 400 iter')
	ax.plot(x_axis, Avg_Physical_Ent_Time_500, marker='o' ,label = r'Phy 500 iter')
	ax.plot(x_axis, Avg_Virtual_Ent_Time_100, marker='o', label = r'Vir 100 iter')
	ax.plot(x_axis, Avg_Virtual_Ent_Time_200, marker='o', label = r'Vir 200 iter')
	ax.plot(x_axis, Avg_Virtual_Ent_Time_300, marker='o', label = r'Vir 300 iter')
	ax.plot(x_axis, Avg_Virtual_Ent_Time_400, marker='o', label = r'Vir 400 iter')
	ax.plot(x_axis, Avg_Virtual_Ent_Time_500, marker='o', label = r'Vir 500 iter')

handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
plt.legend(by_label.values(), by_label.keys(), bbox_to_anchor=(1, 1), loc=2)



#ax.legend(loc = 'right')
plt.xlabel('No. of Hops from Source')
plt.ylabel('Average Entanglement Time')
plt.show()


#Fidelity vs Distance from source( hops from source)
#fig, ax = plt.subplots()

fig = plt.figure()
ax = fig.add_axes([0.1, 0.1, 0.70, 0.75])
ax.xaxis.set_major_locator(MaxNLocator(integer=True))

for i in range(5):
	ax.plot(x_axis, Avg_fidelity_physical_100, marker='o' ,label = r'Phy 100 iter')
	ax.plot(x_axis, Avg_fidelity_physical_200, marker='o' ,label = r'Phy 200 iter')
	ax.plot(x_axis, Avg_fidelity_physical_300, marker='o' ,label = r'Phy 300 iter')
	ax.plot(x_axis, Avg_fidelity_physical_400, marker='o' ,label = r'Phy 400 iter')
	ax.plot(x_axis, Avg_fidelity_physical_500, marker='o' ,label = r'Phy 500 iter')
	ax.plot(x_axis, Avg_fidelity_virtual_100, marker='o', label = r'Vir 100 iter')
	ax.plot(x_axis, Avg_fidelity_virtual_200, marker='o', label = r'Vir 200 iter')
	ax.plot(x_axis, Avg_fidelity_virtual_300, marker='o', label = r'Vir 300 iter')
	ax.plot(x_axis, Avg_fidelity_virtual_400, marker='o', label = r'Vir 500 iter')
	ax.plot(x_axis, Avg_fidelity_virtual_500, marker='o', label = r'Vir 600 iter')

#ax.plot(x_axis, Avg_fidelity_physical, marker='o', alpha= 0.5,  color = 'blue' ,label = r'Fidelity for physical')
#ax.plot(x_axis, Avg_fidelity_virtual, '--' , marker='o',  alpha= 0.5, color = 'red', label = r'Fidelity for virtual')

handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
plt.legend(by_label.values(), by_label.keys(), bbox_to_anchor=(1, 1), loc=2)

#ax.legend(loc = 'upper left')
plt.xlabel('No. of Hops from Source')
plt.ylabel('Average Fidelity')
plt.show()

