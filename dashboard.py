#######################
# Import libraries
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import folium
from streamlit_folium import folium_static
import plotly.express as px

#######################
# Page configuration
st.set_page_config(
    page_title="자살 생각/경험 통계 대시보드",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")


#######################
# Load data
df_experience= pd.read_excel("연령대별자살생각경험.xlsx")
df_reason = pd.read_excel("연령별자살생각원인.xlsx")
df_location = pd.read_excel("지역별자살생각.xlsx")
df_suicide_num = pd.read_excel("지역별자살자수.xlsx")

#######################
# Sidebar
with st.sidebar:
    st.title('자살 생각/경험 통계 대시보드')
    
    year_list = list(df_location.year.unique())[::-1]
    
    selected_year = st.selectbox('Select a year', year_list)
    df_selected_year = df_location[df_location.year == selected_year]
    df_selected_year_sorted = df_selected_year.sort_values(by="suicide", ascending=False)

    color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    selected_color_theme = st.selectbox('Select a color theme', color_theme_list)

#######################
    
#######################
# Plots

# Heatmap
def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
    heatmap = alt.Chart(input_df).mark_rect().encode(
            y=alt.Y(f'{input_y}:O', axis=alt.Axis(title="year", titleFontSize=18, titlePadding=15, titleFontWeight=900, labelAngle=0)),
            x=alt.X(f'{input_x}:O', axis=alt.Axis(title="", titleFontSize=18, titlePadding=15, titleFontWeight=900)),
            color=alt.Color(f'max({input_color}):Q',
                             legend=None,
                             scale=alt.Scale(scheme=input_color_theme)),
            stroke=alt.value('black'),
            strokeWidth=alt.value(0.25),
        ).properties(width=900
        ).configure_axis(
        labelFontSize=12,
        titleFontSize=12
        ) 
    # height=300
    return heatmap


# Convert number to text 
def format_number(num):
    return f'{round(num,1)} %'

# Calculation year-over-year population migrations
def calculate_suicide_rate_difference(input_df, input_year):
  selected_year_data = input_df[input_df['year'] == input_year].reset_index()
  previous_year_data = input_df[input_df['year'] == input_year - 2].reset_index()
  selected_year_data['suicide_rate_difference'] = selected_year_data.suicide.sub(previous_year_data.suicide, fill_value=0)
  return pd.concat([selected_year_data.distinction, selected_year_data.suicide, selected_year_data.suicide_rate_difference], axis=1).sort_values(by="suicide_rate_difference", ascending=False)


#######################
# Dashboard Main Panel
col = st.columns((1.5,8), gap='medium')

with col[0]:
    st.markdown('### 자살 생각 통계')

    # Assuming df_suicide_rate_difference_sorted is already calculated and sorted
    df_suicide_rate_difference_sorted = calculate_suicide_rate_difference(df_location, selected_year)

    # Loop through each row in the DataFrame to display suicide information for each state
    for index, row in df_suicide_rate_difference_sorted.head(5).iterrows():
        state_name = row['distinction']
        state_population = format_number(row['suicide'])  # Assuming this represents the suicide rate
        state_delta = format_number(row['suicide_rate_difference'])  # Difference in suicide rates

        st.metric(label=state_name, value=state_population, delta=state_delta)

with col[1]:
    tab1 ,tab2,tab3= st.tabs(["Map chart", "Heat map", "table map"])

    with tab1:
        m = folium.Map([37.58, 127.0], zoom_start=11)
        pivot_table = pd.pivot_table(df_suicide_num,index="distinction",values=["suicide_num"])
        pivot_table["선택"] = pivot_table["suicide_num"].apply(lambda x: False)

        col1, col2 = st.columns([0.3,0.9])

        with col1:
            st.header("지역별 자살수")
            st.write("\n\n")
            edited_df = st.data_editor(pivot_table)

        edited_df["distinction"] = edited_df.index
        select = list(edited_df[edited_df["선택"]]["distinction"])

        with col2:
            geo_data='./SIDO_MAP_2022.json'
            folium.Choropleth(
                geo_data=geo_data, # 경계선 좌표값이 담긴 데이터
                data=edited_df[edited_df["선택"]], # Series or DataFrame 넣으면 된다
                columns=['distinction','suicide_num'], # DataFrame의 어떤 columns을 넣을지
                key_on='feature.properties.CTP_KOR_NM', # SIG_KOR_NM 값을 가져오겠다.
                fill_color="plasma",
                fill_opacity=0.5, # 색 투명도
                line_opacity=0.5, # 선 투명도
                legend_name='자살 수' # 범례
            ).add_to(m)
            folium_static(m)
    
    with tab2:
        st.markdown('#### 지역별 자살 생각')
        heatmap = make_heatmap(df_location, 'year', 'distinction', 'suicide', selected_color_theme)
        st.altair_chart(heatmap, use_container_width=True)
    
    with tab3:
        st.markdown('#### 지역별 자살 생각')
        st.dataframe(df_selected_year_sorted,
                    column_order=("distinction", "suicide"),
                    hide_index=True,
                    width=None,
                    column_config={
                        "distinction": st.column_config.TextColumn(
                            "distinction",
                        ),
                        "suicide": st.column_config.ProgressColumn(
                            "suicide",
                            format="%f",
                            min_value=0,
                            max_value=max(df_selected_year_sorted.suicide),
                        )}
                    )

#######################
#### 대전시 자살 생각 경험률 #######
def bar_chart(*geo):
    bar_df = edited_df[edited_df["선택"]]
    fig = px.bar(bar_df,
    title="대전시 연령별 자살생각 경험률",
    y="자살 생각 경험률",
    x="연령별",
    color="연령별",
    hover_data="자살 생각 경험률")
    return fig
    
df = pd.read_excel("연령대별자살생각경험.xlsx")
st.title("대전시 자살 생각 경험률")


pivot_table = pd.pivot_table(df,index="연령별",values=["자살 생각 경험률"])
pivot_table["선택"] = pivot_table["자살 생각 경험률"].apply(lambda x: False)


col = st.columns([0.3,0.9])

with col[0]:
    st.write("\n\n")
    edited_df = st.data_editor(pivot_table)
    edited_df["연령별"] = edited_df.index

with col[1]:
    select = list(edited_df[edited_df["선택"]]["연령별"])
    st.plotly_chart(bar_chart(*select))

    


#######################
#### 대전시 자살 생각 원인 #######
# Load data
df = pd.read_excel("연령별자살생각원인.xlsx")
st.title("대전시 자살 생각 원인")
col = st.columns((5,5), gap='medium')
with col[0]:
    # Function to create a bar chart for a given value
    def bar_chart(df, value):
        fig = px.bar(df,
                    title=f"대전시 연령별 자살생각 원인: {value}",
                    y=value,
                    x=df.index,  # assuming the index of df is '연령별'
                    color=df.index,
                    labels={'y': value, 'x': '연령별'},
                    hover_data=[value])
        return fig

    # Create a pivot table
    pivot_table = pd.pivot_table(df, index="연령별", values=[
        "경제적 어려움", "외로움, 고독", "질병 또는 장애",
        "가정불화", "이성문제", "학교 성적, 진학 문제", "사고나 트라우마",
        "친구나 동료들과의 불화 및 따돌림", "기타"
    ])

    # Define the list of values to create graphs for
    values_to_plot = ["경제적 어려움", "외로움, 고독", "질병 또는 장애",
                    "가정불화", "이성문제", "학교 성적, 진학 문제", "사고나 트라우마",
                    "친구나 동료들과의 불화 및 따돌림", "기타"]

    # Let the user choose one value to plot
    selected_reason = st.selectbox('자살 생각이 드는 원인', values_to_plot)

    # Function to create a bar chart for the selected reason
    def bar_chart(pivot_df, reason):
        fig = px.bar(pivot_df, y=reason, title=f"대전시 자살 생각 원인: {reason}")
        return fig

    # Create and display the chart for the selected reason
    st.plotly_chart(bar_chart(pivot_table, selected_reason))

with col[1]:
    age_groups = ["15 ~ 19세", "20 ~ 29세", "30 ~ 39세", "40 ~ 49세", "50 ~ 59세", "60세 이상"]

    def donut_chart_for_age_group(df, age_group):
        age_group_data = df.loc[age_group]
        fig = px.pie(age_group_data,
                    title=f"대전시 {age_group} 자살 생각이 드는 원인",
                    values=age_group_data.values,
                    names=age_group_data.index,
                    hole=0.3)  # Creates the donut chart
        fig.update_traces(textinfo='percent+label')
        return fig


    # Create a donut chart for the "60대 이상" age group and display it
    selected_age_group = st.selectbox('연령별 자살 생각이 드는 원인을 보고 싶은 연령대를 선택하세요:', age_groups)

    # Create and display the donut chart for the selected age group
    st.plotly_chart(donut_chart_for_age_group(pivot_table, selected_age_group))



