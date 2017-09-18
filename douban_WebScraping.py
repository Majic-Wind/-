#!/usr/bin/python
#coding:utf-8

#爬取资料并返回为列表形式
def get_parse_html(url,parent_tap,class_or_id,txt_tap):
    from urllib import request
    from bs4 import BeautifulSoup as bs
    resp = request.urlopen(url)
    html_data = resp.read().decode('utf-8')
    soup = bs(html_data,"html.parser")
    letters_list = soup.find_all( parent_tap, class_ = class_or_id )
    each_list = []
    for i in letters_list:
        if i.find_all(txt_tap)[0].string is not None:
            each_list.append(i.find_all(txt_tap)[0].string.strip())
    return each_list
#只保留汉字
def hanzi_only(letters):
    import re
    pattern = re.compile(r"[\u4e00-\u9fa5]+")
    filter_data = re.findall(pattern,letters)
    cleaned_letters = "".join(filter_data)
    return cleaned_letters
#删除stopwords并统计每组词语的数量
def remove_stopwords_and_summary(df,column,df_stopwords,column_stopword):
    words_df_rm_stopw = df[~df[column].isin(df_stopwords[column_stopword])]
    import numpy as np
    words_stat=words_df_rm_stopw.groupby([column])[column].agg({"计数":np.size})
    words_stat = words_stat.reset_index().sort_values(["计数"],ascending=False)
    return words_stat
#以词云方式显示爬取内容
def draw_wordcloud(letters_summary_dict):
    import matplotlib.pyplot as plt
    #%matplotlib inline
    import matplotlib
    matplotlib.rcParams['figure.figsize'] = (20.0, 10.0)#控制绘制图尺寸
    from wordcloud import WordCloud#词云包
    wordcloud=WordCloud(font_path="simhei.ttf",background_color="white",max_font_size=80)
    wordcloud=wordcloud.fit_words(letters_summary_dict)
    plt.imshow(wordcloud)

def main():
    each_comment_list=[]
    #敦刻尔克影评前8页
    for i in [0,20,42,63,83,106,126,147]:
        requrl = "https://movie.douban.com/subject/26607693/comments?start="+str(i)+"&limit=20&sort=new_score&status=P"
        each_comment_list.append(get_parse_html(requrl,"div","comment","p"))
    #将嵌套列表中所有评论合并为一个字符串
    letters = ""
    for i in range(len(each_comment_list)):
        for k in range(len(each_comment_list[i])):
            letters = letters + str(each_comment_list[i][k])
    #仅提取汉字
    cleaned_comments = hanzi_only(letters)
    #利用jieba分词将字符串拆分为词语
    from jieba import lcut
    segment = lcut(cleaned_comments)

    #加载stopwords并删除stopwords，统计词语数量
    from pandas import DataFrame
    letters_df = DataFrame({"segment":segment})

    from pandas import read_csv
    stopwords=read_csv("stopwords.txt",index_col=False,\
                    quoting=3,sep="\t",names=['stopword'], encoding='utf-8')
    letters_stat = remove_stopwords_and_summary(letters_df,"segment",stopwords,"stopword")
    #转为字典形式，方便传入wordcloud
    word_frequence_dict = {x[0]:x[1] for x in letters_stat.head(1000).values}

    draw_wordcloud(word_frequence_dict)
if __name__=='__main__':
    main()