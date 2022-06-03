#!/usr/bin/env python
# coding: utf-8

# # DATA UNDERSTANDING

# ## **Context**
# 
# Sebuah toko penyewaan DVD film ingin mengetahui gambaran umum tentang kondisi perilaku pelanggannya. Terdapat sebuah database yang menunjukan detail dari proses transaksi penyewaan DVD film oleh para pelanggan. Dari database tersebut, perusahaan ingin bisa mendapatkan insight yang dapat dijalankan, sehingga nantinya mereka dapat melakukan penerapan strategi yang tepat sasaran untuk memperoleh keuntungan yang lebih dari saat ini. Analisa untuk data ini akan berfokus pada customer/pelanggan, dimana dari data hasil sewa yang dilakukan oleh para pelanggan, faktor apa sajakah yang mempengaruhinya. Apakah faktor durasi sewa tiap pelanggan dan jumlah film yang disewa oleh pelanggan akan mempengaruhi hasil sewa dari para pelanggan?
# 
# ## **Database Information**
# 
# Database yang digunakan adalah database ``sakila``, dengan fokus analisanya yaitu ``customer``.
# 
# Sumber Database: https://dev.mysql.com/doc/sakila/en/sakila-installation.html
# 
# Database yang dimiliki mempunyai beberapa tabel, antara lain:
# - Customer      : Menyimpan informasi tentang data pelanggan/customer.
# - Address       : Menyimpan informasi tentang alamat pelanggan/customer.
# - City          : Menyimpan informasi tentang kota pelanggan/customer.
# - Country       : Menyimpan informasi tentang negara pelanggan/customer.
# - Payment       : Menyimpan informasi tentang pembayaran yang dilakukan oleh pelanggan/customer.
# - Rental        : Menyimpan informasi tentang penyewaan DVD film yang dilakukan oleh pelanggan/customer.
# - Inventory     : Menyimpan informasi tentang data inventaris yang berisi setiap salinan film tertentu di toko tertentu.
# - Film          : Menyimpan informasi tentang daftar semua film yang berpotensi tersedia di toko-toko. Salinan stok aktual dari setiap film disajikan dalam tabel inventaris.
# 
# Setiap tabel yang tertera pada database dapat terhubung, baik secara langsung maupun tidak langsung, sehingga setiap informasi dari database ini akan dapat saling berkaitan.

# # DATA BASE

# ## **Connecting To Database**
# 
# Bagian ini merupakan langkah awal untuk mulai melakukan proses analisis data. Pertama adalah membuat koneksi ke database di mana seperti yang sudah dijelaskan sebelumnya, database yang akan digunakan adalah database ``sakila``. Dengan melakukan koneksi ini, kita dapat mengakses seluruh tabel yang ada pada database.

# In[48]:


# Import Modules

import mysql.connector
import pandas as pd
import numpy as np


# In[49]:


# Connect To Database

mydb = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = 'root',
    database = 'sakila'
)


# Selain melakukan koneksi ke database, hal lain yang perlu dilakukan pada bagian awal ini adalah membuat sebuah fungsi untuk menuliskan query yang kemudian akan disimpan dalam bentuk DataFrame. Tujuannya adalah agar data hasil query yang dibuat dapat disimpan dan digunakan untuk keperluan analisis data. Nantinya, di sini terdapat 2 query untuk mengambil data-data yang ada di database, bukan hanya berasal dari 1 tabel, tapi juga akan melibatkan hubungan antar tabel.

# In[50]:


# Querry Function

mycursor = mydb.cursor()

def sql_df(yourQuerry):
    mycursor.execute(yourQuerry)
    myresult = mycursor.fetchall()
    df = pd.DataFrame(myresult, columns = mycursor.column_names)
    return df


# ## **Data Transaksi Penyewaan DVD Film**
# 
# Data ini merupakan gabungan dari tabel, yaitu tabel ```customer```, ```address```, ```city```, ```country```, ```payment```, ```rental```, dan ```film```. Masing-masing dari setiap tabel tersebut diambil beberapa kolomnya dan tidak diambil secara keseluruhan. Informasi-informasi yang dianggap penting saja lah yang diambil. Informasi yang diambil antara lain adalah :
# - customer_id dari tabel customer
# - first_name dari tabel customer
# - last_name dari tabel customer
# - email dari tabel customer
# - address dari tabel address
# - phone dari tabel address
# - city dari tabel city
# - country dari tabel country
# - amount dari tabel payment
# - payment_date dari tabel payment
# - rental_date dari tabel rental
# - return_date dari tabel rental
# 
# Semua informasi tersebut kemudian dijadikan dalam sebuah DataFrame yang nantinya akan diolah informasinya.

# In[51]:


# Querry 1

table1 = sql_df('''
select c.customer_id, c.first_name, c.last_name, concat(c.first_name,' ',c.last_name) as name, c.email,
    a.address, a.phone,
    ci.city,
    co.country,
    sum(p.amount) as payment_total, p.payment_date,
    r.rental_date, r.return_date,
    count(f.title) as total_film
from customer c
join address a on c.address_id = a.address_id
join city ci on a.city_id = ci.city_id
join country co on ci.country_id = co.country_id
join payment p on c.customer_id = p.customer_id
join rental r on c.customer_id = r.customer_id
join inventory i on r.inventory_id = i.inventory_id
join film f on i.film_id = f.film_id
join film_category fc on f.film_id = fc.film_id
join category cf on fc.category_id = cf.category_id
group by customer_id;
''')

table1


# ## **Data Harga Pembayaran Dan Jumlah DVD Film Yang Disewa Oleh Pelanggan**
# 
# Data ini merupakan informasi yang bisa menjadi data tambahan untuk melihat gambaran tentang data yang dimiliki. Data ini memuat nama pelanggan, jumlah film yang disewa, dan total pembayarannya untuk masing-masing pelanggan.

# In[52]:


# Querry 2

table2 = sql_df('''
select concat(c.first_name,' ',c.last_name) as Nama, count(f.title) as Jumlah_Film_Yang_Disewa,
sum(p.amount) as Total_Pembayaran
from customer c
join payment p on c.customer_id = p.customer_id
join rental r on c.customer_id = r.customer_id
join inventory i on r.inventory_id = i.inventory_id
join film f on i.film_id = f.film_id
group by Nama
order by Jumlah_Film_Yang_Disewa desc;
''')

table2


# ## **Data Pelanggan Yang Melebihi Waktu Peminjaman**
# 
# Data ini memuat informasi nama pelanggan beserta alamat dan nomor teleponnya yang melakukan peminjaman DVD film melebihi durasi yang telah ditentukan. Sehingga penyewa DVD film perlu menghubungi pelanggan tersebut agar segera mengembalikan DVD film yang telah dipinjamnya.

# In[47]:


# Querry 3

table3 = sql_df('''
select concat(c.first_name,' ',c.last_name) as Nama, c.email as Email, a.address as Alamat, a.phone as Telepon
from rental r join customer c on r.customer_id = c.customer_id
join address a on c.address_id = a.address_id
join inventory i on r.inventory_id = i.inventory_id
join film f on i.film_id = f.film_id
where r.return_date is null
and rental_date + interval f.rental_duration day < current_date()
group by Nama
order by f.title
;
''')

table3


# ## **Data Pelanggan Yang Memiliki Rata-Rata Pembayaran Lebih Dari Rata-Rata Keseluruhan Pembayaran**
# 
# Data ini berisi data pelanggan yang memiliki nilai rata-rata transaksi pembayaran melebihi rata-rata seluruh pembayaran pelanggan. Hal ini dimaksudkan supaya penyewa film mampu mengetahui pelanggan mana saja yang mampu memberikan keuntungan lebih pada bisnisnya.

# In[53]:


# Querry 4 (CTE)

sql_df('''
with payment_avg as (
select avg(amount) as avg_payment
from payment)

select concat(c.first_name,' ',c.last_name) as Nama, avg(p.amount) as Pembayaran
from customer c
join payment p on c.customer_id = p.customer_id
group by Nama
having avg(p.amount) >= (select avg_payment from payment_avg)
order by Pembayaran desc;
''')


# # DATA MANIPULATION

# Seperti yang telah dijelaskan sebelumnya, data yang digunakan untuk dianalisis adalah data pada ```table1```. Sebelum melakukan analisis lebih lanjut, hal yang harus dilakukan adalah mengecek informasi serta anomali pada data. Jika memang terdapat hal-hal yang dianggap 'kotor' pada data, maka yang perlu dilakukan adalah melakukan penanganan pada bagian tersebut. Pada bagian ini, data akan 'dibersihkan', sehingga output akhir yang diharapkan adalah terdapat sebuah dataset yang bersih yang dapat dianalisis lebih lanjut dengan menampilkan visualisasi, serta melihat statistics-nya.

# ## **Data Anomalies**

# In[6]:


# Check Info Tabel1

table1.info()


# ## **Melihat Data Sekilas Dari General Info**
# 
# Dari info diatas terlihat bahwa secara keseluruhan terdapat 599 baris data dengan total 14 kolom. Setiap kolomnya memiliki tipe data yang berbeda-beda. Ada object, integer, dan datetime. Jika melihat informasi pada non-null values atau data yang tersedia pada setiap kolomnya tersebut, semua kolom atau feature memiliki data yang lengkap. Namun, pada informasi tipe data, ada satu tipe data yang salah yaitu pada kolom ```payment_total```.

# In[7]:


# Check Missing Value Percentage

table1.isnull().sum()


# ## **Missing Values**
# 
# Dari pengecekan missing values diatas juga terlihat bahwa tidak ada data yang berbeda. Sehingga kita tidak perlu melakukan penanganan untuk jumlah data yang berbeda.

# ## **Mengubah Tipe Data Yang Salah**
# 
# Pada general info sebelumnya telah diketahui bahwa ada tipe data yang tidak sesuai. Kolom features tersebut terlebih dahulu diubah agar fungsionalitasnya kembali ke hakekatnya. Tujuannya tentu saja agar features tersebut dapat dipergunakan sebagaimana mestinya.

# In[8]:


# Change Spesific Column To Numeric Format

table1['payment_total'] = pd.to_numeric(table1['payment_total'])


# In[9]:


# Recheck Info

table1.info()


# ## **Recheck Data Information**
# 
# Bagian sebelumnya, features yang memiliki tipe data yang salah sudah diubah ke dalam tipe data yang seharusnya. Untuk memastikannya, output di atas merupakan informasi umum yang kembali diperlihatkan untuk memastikan tipe data yang sudah diubah tersebut. Features yang seharusnya bertipe data numerik, yaitu payment_total sudah menjadi tipe data float64. Dengan begini, perubahan yang dilakukan sebelumnya sudah terimplementasi dan anomali data sudah teratasi.

# In[10]:


# Check Duplicate

table1[table1.duplicated()]


# ## **Data Duplicate**
# 
# Anomali berikutnya yang bisa ditemui adalah data yang duplikat. Tentu saja data yang bersifat duplikat ini akan menjadi sesuatu hal yang akan mengganggu proses analisis data. Jika memang nantinya terdapat data yang duplikat, sebaiknya data duplikatnya dihapus dan disisakan data yang unique saja. Untuk data saat ini, melihat output di atas artinya tidak terdapat data yang duplikat. Dengan begitu tidak perlu ada action yang dilakukan.

# ## **Features 'rental_time'**
# 
# Data awal menunjukan terdapat beberapa features yang merupakan tipe data datetime. Artinya, kita dapat melakukan ekstraksi informasi tambahan dari kedua features tersebut. Sebelumnya, kita perlu tahu dulu definisi dari kedua tabel tersebut. rental_date secara singkat dapat diartikan sebagai waktu penyewaan oleh pelanggan, sedangkat return_date adalah waktu pelanggan mengembalikan DVD film yang telah disewanya. 
# 
# Melihat kedua definisi tersebut, sebuah informasi dapat diambil yaitu seberapa lama waktu peminjaman DVD film yang dilakukan oleh para pelanggan dari waktu peminjaman hingga waktu pengembalian. Oleh karena itu, untuk mendapatkan informasinya, maka perlu dilakukan pengurangan antara return_date dengan rental_date. Mungkin akan timbul pertanyaan, apakah waktu dapat dikurangkan? Jawabannya, bisa. Output yang keluar nantinya akan berupa selisih atau lamanya waktu proses tersebut dalam satuan hari.

# In[55]:


# Add New Column (Rental Time)

from datetime import datetime

table1['rental_time'] = (table1['return_date'] - table1['rental_date']).dt.days 
table1


# ## **Unique Value 'rental_time'**
# 
# Setelah membuat sebuah kolom baru yang bernama rental_time sebagaimana yang sudah didefinisikan sebelumnya, mari kita cek bagaimana data tersebut. Jika melihat dari preview output sebelumnya, tidak ada keanehan. Lantas bagaimana jika kita melihat lebih dalam ke dalam feature baru ini? Berikut ini penampakan hasil yang memperlihatkan unique values beserta jumlah data di setiap unique values-nya.
# 
# Dan terlihat dari hasil berikut tidak ada anomali data pada kolom rental_time. Oleh karena itu, data ini bisa dipertahankan dan bisa dilakukan analisia selanjutnya.

# In[56]:


# Check Data Anomalies in Date Time Format

table1['rental_time'].value_counts()


# ## **Preview Cleaned Data**
# 
# Setelah semua anomalies sudah diselesaikan, artinya data yang dimiliki sudah bersih. Di bawah ini adalah sample data yang dianggap sudah bersih setelah melewati proses-proses sebelumnya.

# In[13]:


# Clean Data

table1.sample(20)


# ## **General Info Cleaned Data**
# 
# Berikut ini merupakan informasi umum dari data yang telah dibersihkan dari anomali-anomali sebelumnya.

# In[57]:


# Check Some Info

listItem = []
for col in table1.columns :
    listItem.append([col, table1[col].dtype, len(table1),table1[col].isna().sum(),
                    round((table1[col].isna().sum()/len(table1[col])) * 100,2),
                    table1[col].nunique(), list(table1[col].drop_duplicates().sample(2).values)])

table1Desc = pd.DataFrame(columns=['Column Name', 'Data Type', 'Data Count', 'Missing Value', 
    'Missing Value Percentage', 'Number of Unique', 'Unique Sample'],
                     data=listItem)
table1Desc


# ## **Payment Total Berdasarkan Rental Time**

# In[15]:


# Groupping and Aggregating

table1[['payment_total','rental_time']].groupby('rental_time').describe()


# Berdasarkan agregasi dan pengelompokan data antara features payment_total dengan rental_time diatas, kita dapat mengetehaui beberapa informasi.
# Terdapat sebuah feature yang bernama 'rental_time' pada dataset. Feature ini merupakan durasi peminjaman DVD film yang dilakukan oleh para pelanggan dengan satuan hari yang pada database. Feature 'rental_time' ini terdiri dari beberapa kategori durasi peminjaman, mulai dari hari ke-0 hingga hari ke-9.
# Dari tabel diatas dapat diambil informasi bahwa rata-rata pelanggan melakukan peminjaman DVD film selama 1 hari, dengan total 'rental_time' nya yaitu sebanyak 81. Namun, banyaknya waktu peminjaman tidak mempengaruhi jumlah pembayaran yang dilakukan oleh pelanggan. Dimana dari data tabel tersebut, untuk rata-rata total biaya peminjaman DVD film yaitu sekitar 3.413 dengan durasi peminjamannya yaitu selama 3 hari.

# # **DATA VISUALIZATION & STATISTICS**

# ## **Statistik Deskriptif**

# In[20]:


import matplotlib.pyplot as plt
import seaborn as sns
import statistics as st
from collections import Counter
sns.set(style="darkgrid")


# Berikut ini merupakan deskriptif statistik data untuk data numerik yang ada pada tabel sebelumnya. Statistik deskriptif ini menggunakan fungsi ``.describe()`` dan akan menampilkan informasi statistik antara lain : ``jumlah data``, ``rata-rata``, ``standar deviasi``, ``nilai minimum``, ``kuartil 1``, ``kuartil 2``, ``kuartil 3``, dan ``nilai maksimum``.

# In[21]:


table1[['payment_total', 'total_film', 'rental_time']].describe().transpose()


# In[22]:


def central_tendency(column):
  data = {}
  data['Column'] = column.name
  data['Mean'] = st.mean(column)
  data['Mode'] = Counter(column).most_common()[0][0]
  data['Median'] = st.median(column)
  return pd.DataFrame([data])

def dispersion(column):
  data = {}
  data['Column'] = column.name
  data['Variance'] = st.variance(column)
  data['Standard Deviation'] = st.stdev(column)
  data['Skew'] = column.skew()
  return pd.DataFrame([data])

def plot_distribution(column):
  f, (ax_box, ax_hist) = plt.subplots(2, sharex=True, figsize=(10, 6),
                                      gridspec_kw={"height_ratios": {0.2, 1}})
  
  info = central_tendency(column)
  mean = info['Mean'].values[0]
  median = info['Median'].values[0]
  mode = info['Mode'].values[0]

  sns.boxplot(x=column, ax=ax_box)
  ax_box.axvline(mean, color='r', linestyle='--')
  ax_box.axvline(median, color='g', linestyle=':')
  ax_box.axvline(mode, color='b', linestyle='-')
  ax_box.set(xlabel='')

  sns.histplot(x=column, ax=ax_hist, kde=True)
  ax_hist.axvline(mean, color='r', linestyle='--')
  ax_hist.axvline(median, color='g', linestyle=':')
  ax_hist.axvline(mode, color='b', linestyle='-')

  plt.legend({'Mean':mean, 'Median':median, 'Mode':mode})
  plt.show()


# ## **Ukuran Pemusatan Data**
# 
# Ukuran Pusat Data atau Central Tendency merupakan ringkasan data yang menggambarkan posisi sentral dari distribusi frekuensi untuk sekelompok data. Kita bisa mendeskripsikan ukuran pusat data ini dengan menggunakan, misalnya ``mean`` atau rata-rata, ``median`` atau nilai tengah, dan ``mode`` atau nilai yang sering muncul.

# In[23]:


pd.concat([central_tendency(table1['payment_total']),
           central_tendency(table1['total_film']),
           central_tendency(table1['rental_time']) ], ignore_index=True)


# ## **Ukuran Penyebaran Data**
# 
# Ukuran Penyebaran Data atau Measure of Spread merupakan ringkasan yang menggambarkan seberapa tersebar data kita. Kita bisa mendeskripsikan penyebaran data ini dengan ``range`` atau rentang nilai, ``kuartil``, ``varians``, dan ``standar deviasi``.

# In[24]:


pd.concat([dispersion(table1['payment_total']),
           dispersion(table1['total_film']),
           dispersion(table1['rental_time']) ], ignore_index=True)


# ## **Ukuran Distribusi Data**
# 
# Ukuran distribusi data merupakan ringkasan yang menggambarkan pembagian data yang kita miliki. Kita bisa mendeskripsikan distribusi data dengan menggunakan grafik berupa histogram atau barplot, dan menggunakan pengujian statistik.
# Pada grafik histogram, data yang terdistribusi normal akan memiliki bentuk kurva yang simetris dengan titik pusat berada di rata-ratanya (μ) dan penyebaran datanya secara standar deviasi (σ) lebih banyak di dekat nilai rata-rata. Sedangkan pada uji statistik, data yang terdistribusi normal akan memiliki nilai ``p-value`` lebih besar dari 0.05.

# In[25]:


plot_distribution(table1['payment_total'])


# In[26]:


plot_distribution(table1['total_film'])


# In[27]:


plot_distribution(table1['rental_time'])


# Berdasarkan grafik yang telah dibuat diatas, dapat disimpulkan bahwa feature ``payment_total``,  ``total_film``, dan  ``rental_time`` memiliki distribusi data yang tidak normal. Dan pada feature ``payment_total`` dan ``total_film`` juga masih ada beberapa outlier. Kita perlu melakukan penanganan terhadap outlier-outlier tersebut supaya datanya bisa dianalisis lebih lanjut.

# ## **Mencari Data Outlier Dan Penanganannya**

# In[28]:


def find_outlier(column):
  Q1 = column.quantile(0.25)
  Q3 = column.quantile(0.75)
  IQR = Q3 - Q1
  outliers = []

  for data in column:
    if (data > (Q3 + 1.5 * IQR)) | (data < (Q1 - 1.5 * IQR)):
      outliers.append(data)

  return outliers


# In[29]:


outliers_payment_total = find_outlier(table1['payment_total'])
outliers_total_film = find_outlier(table1['total_film'])

print('Outliers_payment_total =', outliers_payment_total)
print('Outliers_total_film =', outliers_total_film)


# In[30]:


table1_cleaned = table1[~table1['total_film'].isin(outliers_total_film)]
print('Before removing outliers total film:', table1.shape)
print('After removing outliers total film:', table1_cleaned.shape)


# In[31]:


table2_cleaned = table1_cleaned[~table1_cleaned['payment_total'].isin(outliers_payment_total)]
print('Before removing outliers payment total:', table1_cleaned.shape)
print('After removing outliers payment total:', table2_cleaned.shape)


# Dari hasil diatas terlihat bahwa feature ``payment_total`` memiliki 14 data outlier. Sedangkan untuk feature ``total_film`` memiliki 10 data outlier. Lalu, setelah kita melakukan pengahapusan data outlier tersebut, data kita yang semula terdiri dari 599 baris dengan 15 kolom berubah menjadi terdiri dari 585 baris dengan 15 kolom.

# ## **Recheck Distribusi Data**

# In[32]:


table_cleaned = table2_cleaned

pd.concat([dispersion(table_cleaned['payment_total']),
           dispersion(table_cleaned['total_film']),
           dispersion(table_cleaned['rental_time']) ], ignore_index=True)


# In[33]:


plot_distribution(table_cleaned['payment_total'])


# In[34]:


plot_distribution(table_cleaned['total_film'])


# Dari grafik diatas terlihat bahwa data outlier sudah tidak ada lagi. Selanjutnya kita akan menganalisis data yang telah bersih sesuai dengan keperluan kita dan melakukan visualisasi data.

# ## **Uji Normalitas Data**

# In[35]:


from scipy.stats import normaltest

kolom = ['payment_total', 'total_film', 'rental_time']
p_value = []
distribusi=[]
for i in kolom:
    stats, pval=normaltest(table_cleaned[i])
    p_value.append(pval)
    if pval>0.05:
        distribusi.append('normal')
    else:
        distribusi.append('tidak normal')
        
pd.DataFrame({'p_value':p_value, 'distribusi':distribusi},index=kolom)


# Sebelumnya kita telah melakukan pengukuran distribusi data secara grafik. Selanjutnya kita melakukan pengukuran distribusi data dengan menggunakan uji statisik.
# Dari uji normalitas data diatas dapat disimpulkan bahwa feature ``payment_total``, ``total_film``, dan ``rental_film`` memiliki distribusi data yang tidak normal dikarenakan nilai p-value dari ketiga features tersebut lebih kecil dari 0.05.
# Hal ini bisa dikatakan ketiga features tersebut termasuk dalam kategori non-parametrik. 

# ## **Uji Hipotesis**

# In[37]:


Ho = 'Tidak Ada Perbedaan Jumlah Pembayaraan Dari Masing-Masing Durasi Peminjaman'
Ha = 'Ada Perbedaan Jumlah Pembayaraan Dari Masing-Masing Durasi Peminjaman'

from scipy.stats import kruskal

result = list(kruskal(
    table_cleaned[table_cleaned['rental_time'] == 0]['payment_total'],
    table_cleaned[table_cleaned['rental_time'] == 1]['payment_total'],
    table_cleaned[table_cleaned['rental_time'] == 2]['payment_total'],
    table_cleaned[table_cleaned['rental_time'] == 3]['payment_total'],
    table_cleaned[table_cleaned['rental_time'] == 4]['payment_total'],
    table_cleaned[table_cleaned['rental_time'] == 5]['payment_total'],
    table_cleaned[table_cleaned['rental_time'] == 6]['payment_total'],
    table_cleaned[table_cleaned['rental_time'] == 7]['payment_total'],
    table_cleaned[table_cleaned['rental_time'] == 8]['payment_total'],
    table_cleaned[table_cleaned['rental_time'] == 9]['payment_total'],
))

print('U-statistic:', result[0])
print('P-Value:', result[1])
print('Kesimpulan :')

if result[1] <= 0.05:
    print('Tolak Ho, artinya', Ha)
else:
    print('Terima Ho, artinya', Ho)


# In[38]:


#Pengecekan

cek = table_cleaned[['rental_time','payment_total']].groupby('rental_time').median()
cek.sort_values('payment_total', ascending = False, inplace = True)
cek


# Dari pengujian normalitas data sebelumnya telah dihasilkan bahwa data-data tersebut tidak terdistribusi normal dan merupakan data non-parametrik. Sehingga pada uji hipotesis ini digunakanlah uji hipotesis ``Kruskal-Wallis``, karena digunakan untuk menguji hipotesis rata-rata di lebih dari dua populasi. Pada uji hipotesis ini kita akan menguji sebagi Ho nya apakah jumlah pembayaran dari masing-masing durasi peminjaman memiliki nilai yang sama.
# Berdasarkan hail uji yang telah dilakukan, kesimpulan yang didapat adalah ``Terima Ho``, yang berarti tidak ada perbedaan jumlah pembayaraan dari masing-masing durasi peminjaman atau setiap durasi peminjaman memiliki jumlah pembayaran yang sama. Lalu kita mencoba untuk mengecek dari kedua feature tersebut, dan dari pengecekan dapat dilihat masing-masing jumlah pembayaran di setiap durasi peminjaman memiliki perbedaan namun sangat lah kecil. Sehingga dikatakan bahwa tidak ada perbedaan dari jumlah pembayaran di masing-masing durasi peminjaman. 

# ## **Hubungan Antara Jumlah Pembayaran, Film Yang Disewa, Dan Waktu Penyewaan**

# In[44]:


plt.figure(figsize=(10,8))
sns.scatterplot(data=table_cleaned, x='total_film', y='payment_total')
plt.title('Korelasi Jumlah Film Yang Disewa Oleh Pelanggan Dengan Total Pembayaran', size=15)
plt.xlabel('Total Film Yang Disewa', size = 15)
plt.ylabel('Total Pembayaran', size = 15)
plt.show()


# In[59]:


plt.figure(figsize=(10,8))
sns.barplot(data=table_cleaned, x='rental_time', y='payment_total')
plt.title('Korelasi Waktu Penyewaan Dengan Total Pembayaran', size=15)
plt.xlabel('Durasi Sewa (Hari)', size = 15)
plt.ylabel('Total Pembayaran', size = 15)
plt.show()


# In[61]:


correlation = table_cleaned[['payment_total', 'total_film', 'rental_time']].corr(method = 'spearman')
correlation


# In[63]:


plt.figure(figsize=(10,10))
sns.heatmap(correlation, annot=True)
plt.title('Korelasi Antara Total Pembayaran Dengan Jumlah Film Yang Disewa Dan Durasi Peminjaman', size=15)
plt.show()


# Berdasarkan ketiga grafik diatas antara lain scatterplot yang memvisualisasikan antara feature ``payment_total`` dengan ``total_film``, barplot yang memvisualisasikan antara feature ``payment_total`` dengan ``rental_film`` dan heatmap yang memvisualisasikan hubungan antara ketiga features tersebut, dapat disimpulkan bahwa jumlah film yang disewa oleh tiap pelanggan memiliki pengaruh positif yang sangat besar terhadap jumlah hasil pembayaran sewa oleh para pelanggan. Namun, untuk durasi sewa memiliki nilai korelsi yang sangat kecil terhadap jumlah hasil pembayaran yang berarti lamanya pelanggan dalam melakukan sewa tidak berpengaruh besar terhadap nilai jumlah pembayaran yang diberikan oleh masing-masing pelanggan.  

# ## **Top 5 Pelanggan Dengan Pembayaran Terbanyak**
# 
# Berikut ini merupakan Data Top 5 Customer/Pelanggan yang melakukan transaksi pembayaran terbanyak. Oleh karena itu, pihak penyewa perlu lebih memperhatikan pelanggan-pelanggan yang melakukan transaksi pembayaran yang banyak tersebut agar pelanggan tersebut senantiasa melakukan transaksi di toko si penyewa. Salah satu caranya adalah dengan memberikan diskon atau potongan harga kepada para pelanggan tersebut.

# In[161]:


top = table_cleaned[['name','payment_total']].groupby('name').sum()
top.sort_values('payment_total', ascending = False, inplace=True)
top.head(5)


# In[42]:


top_customer = table_cleaned[['name','payment_total']].groupby('name').sum().sort_values('payment_total', ascending = False)
top_customer = top_customer.head(5)

x = top_customer.index
y = top_customer['payment_total']

plt.style.use('seaborn')
plt.figure(figsize = (20,10))
plt.barh(x,y, color = sns.color_palette('bright'))
plt.title('Top 5 Pelanggan Dengan Pembayaran Terbanyak', size = 30)
plt.xlabel('Total Pembayaran', size = 15)
plt.ylabel('Nama Pelanggan', size = 15)
plt.show()


# ## **Top 5 Pelanggan Dengan Peminjaman Film Terbanyak**
# 
# Berikut ini merupakan Data Top 5 Customer/Pelanggan yang melakukan penyewaan film terbanyak. Oleh karena itu, pihak penyewa perlu lebih memperhatikan pelanggan-pelanggan yang melakukan banyak pinjaman film tersebut agar pelanggan tersebut tetap selalu melakukan peminjaman film di toko si penyewa. Salah satu caranya adalah dengan memberikan promo atau giveaway kepada para pelanggan tersebut.  

# In[163]:


top_rentfilm = table_cleaned[['name','total_film']].groupby('name').sum()
top_rentfilm.sort_values('total_film', ascending = False, inplace=True)
top_rentfilm.head(5)


# In[41]:


top_rentfilm = table_cleaned[['name','total_film']].groupby('name').sum().sort_values('total_film', ascending = False)
top_rentfilm = top_rentfilm.head(5)

x = top_rentfilm.index
y = top_rentfilm['total_film']

plt.style.use('seaborn')
plt.figure(figsize = (20,10))
plt.bar(x,y, color = sns.color_palette('bright'))
plt.title('Top 5 Pelanggan Dengan Peminjaman Film Terbanyak', size = 30)
plt.xlabel('Nama Pelanggan', size = 15)
plt.ylabel('Total Film Yang Disewa', size = 15)
plt.show()


# In[ ]:




