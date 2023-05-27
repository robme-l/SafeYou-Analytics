import altair as alt
import pandas as pd
from analytics import data
from django.utils.safestring import SafeString

# ------------ PAGE 1 ------------ #
def get_userpage_visualizations(df):
    args = {#"metrics":get_userpage_metrics(df),
            "graphs":get_userpage_graphs(df),
            "VEGA_VERSION":alt.VEGA_VERSION,
            "VEGAEMBED_VERSION":alt.VEGAEMBED_VERSION,
            "VEGALITE_VERSION":alt.VEGALITE_VERSION}
    return args

def resolve_graph(graph):
    return graph.resolve_legend(
                                    color="independent",
                                ).resolve_axis(
                                    x="independent",
                                    y="independent",
                                ).resolve_scale(
                                    color="independent",
                                    x="independent",
                                    y="independent",
                                    theta="independent",
                                )

def get_userpage_graphs(df):
    base = alt.Chart(df)
    reg_chart = get_registration_chart(base)
    devices_chart = get_devices_chart(base)
    lang_chart = get_languages_chart(base)
    age_marital_chart = get_age_marital_chart(base)
    metrics_bar = get_metrics_bar(base)
    graph = (resolve_graph(metrics_bar | 
                alt.vconcat(
                    (resolve_graph(alt.hconcat(reg_chart, 
                                               devices_chart,
                                                spacing=60))),
                    (resolve_graph(alt.hconcat(lang_chart, 
                                               age_marital_chart,
                                                spacing=60))),spacing=60,)
            ).configure(
                background="#FFFCF9",
                padding=0,
            ).configure_title(
                anchor="start",
                color="#6B007B",
            ).configure_axis(
                grid=False,
                domain=False,
                title=None,
                ticks=False,
            ).configure_view(
                strokeWidth=0,
            ))
    graph = SafeString(graph.to_json())
    graphs = {
        ("userpage_graph"):graph,
    }

    return graphs

# ----- CHARTS ----- #
# TODO: add button functionality
def get_registrations(registration_frequency):
    if registration_frequency == "Daily":
        x_string = "yearmonthdate(created_at):T"
    elif registration_frequency == "Monthly":
        x_string = "yearmonth(created_at):T"
    else:
        x_string = "year(created_at):T"
    return x_string

def get_registration_chart(base):
    registration_frequency = 'Daily'
    # TODO: frequency filtering, default is daily
    x_string = get_registrations(registration_frequency)
    color_scale = alt.Scale(
        domain=[2020,2021,2022,2023],
        range=["#9F7F9F","#E7EE4F","#F16C8B","#6B007B"],
    )

    reg_chart = base.mark_line(interpolate="monotone",point=True).encode(
            x = alt.X(x_string,
                      axis=alt.Axis(format="%b %Y",
                                    labelBound=True,
                                    labelSeparation=20,)
            ), y = alt.Y("count():Q",
            ), color=alt.Color("year(created_at):N",
                                legend=alt.Legend(title="Year",titleColor="#605E5C",
                                                    titleFontWeight="bold",
                                                    titleOrient="left",
                                                    orient="none",
                                                    direction="horizontal",
                                                    symbolType="circle",
                                                    legendX=-10,legendY=-30,
                                                    ),
                                scale=color_scale
            ),tooltip="count():Q",
        ).properties(
            title=alt.Title(
                text="Number of Users by Registration Date and Year",
                offset=10,
            ),height=200,width=600,).interactive()

    return reg_chart

def get_devices_chart(base):
    color_scale = alt.Scale(
        domain=["Android","iOS"],
        range=["#9F7F9F","#31AFD4"]
    )
    base = base.encode(
            theta=alt.Theta("count():Q",stack=True),
            color=alt.Color("device_type:N",
                            legend=alt.Legend(title=None,
                                              orient="none",
                                              direction="horizontal",legendX=-10,legendY=-30),
                            scale=color_scale,
            ),tooltip="count():Q",
            
        ).properties(
            title=alt.Title(text="Apple or Android?",offset=10),
            height=200,
        )
    
    pie = base.mark_arc(outerRadius=80)
    text = base.mark_text(
                radius=100, 
                size=10,
            ).transform_aggregate(
                count="count():Q",
                groupby=['device_type']
            ).transform_joinaggregate(
                total_devices='sum(count)',
            ).transform_calculate(
                perc="datum.count / datum.total_devices",
            ).encode(
                text=alt.Text("perc:Q",format=".2%",),
                color=alt.value("#605E5C"),
                tooltip=alt.Text("count:Q"),
            )
    device_chart = alt.layer(pie, text)

    return device_chart

def get_languages_chart(base):
    color_scale = alt.Scale(
        domain=["Armenian","English","Russian"],
        range=["#9F7F9F","#E7EE4F","#31AFD4"]
    )
    base = base.encode(
            theta=alt.Theta("count():Q",stack=True),
            color=alt.Color("language_id:N",
                            legend=alt.Legend(title=None,
                                              orient="none",
                                              direction="horizontal",legendX=-10,legendY=-50),
                            scale=color_scale,
            ),tooltip="count():Q",
            
        ).properties(
            title=alt.Title(text="Which Language Our Users Prefer",offset=10),
            height=200,
        )
    
    donut = base.mark_arc(innerRadius=60,outerRadius=100)
    text = base.mark_text(
                radius=120, 
                size=10,
                fill="#605E5C",
            ).transform_aggregate(
                count="count():Q",
                groupby=['language_id']
            ).transform_joinaggregate(
                total_langs='sum(count)',
            ).transform_calculate(
                perc="datum.count / datum.total_langs",
            ).encode(
                text=alt.Text("perc:Q",format=".2%",
                              bandPosition=0.5),
                tooltip=alt.Text("count:Q"),
            )
    lang_chart = alt.layer(donut, text)

    return lang_chart

def get_age_marital_chart(base):
    x_scale = alt.Scale(
        domain=["10-14","15-19","20-24","25-29","30-34",
                "35-39","40-44","45-49","50-54","55-59",
                "60-64","65+"]
    )
    color_scale = alt.Scale(
        domain=["Married","Not Married","Not Selected"],
        range=["#6B007B","#808080","#CCCCCC"],
    )
    base = base.encode(
        x=alt.X("age_bucket",scale=x_scale,axis=alt.Axis(labelAngle=0)),
        y=alt.Y("count():Q",axis=alt.Axis(labels=False)),
        color=alt.Color("marital_status:N",scale=color_scale,
                        legend=alt.Legend(title="Year",titleColor="#605E5C",
                                                    titleFontWeight="bold",
                                                    titleOrient="left",
                                                    orient="none",
                                                    direction="horizontal",
                                                    symbolType="circle",
                                                    legendX=-10,legendY=-50,
                                                    ),
                        ),
        order=alt.Order("marital_status",sort='ascending'),
        text=alt.condition("datum.marital_status == 'Married'",alt.Text("count():Q"),alt.value('')),
    ).properties(
        title=alt.Title(
                text="Users by Age Group and Marital Status",
                offset=10,
            ),
        height=200,width=600,
    )

    hist = base.mark_bar().encode(tooltip="count():Q")
    text = base.mark_text(fill="white",dy=10)
    total_count = base.mark_text(fill="black"
                ).encode(
                    text="count:Q",
                    y="count:Q",
                    yOffset=alt.value(-7),
                ).transform_aggregate(
                    count="count():Q",
                    groupby=['age_bucket']
                )
    total_box = base.mark_rect(color="orange",
                               cornerRadius=5
                               ).encode(y="count:Q",
                                        ).transform_aggregate(
                                                count="count():Q",
                                                groupby=['age_bucket']
                                            )
    
    worldbank_disclaimer = alt.Chart().mark_text(align="left",
                              baseline="bottom",
                              fontSize=11,fill="#231F20").encode(
                                x=alt.value(40),
                                y=alt.value(230),
                                text=alt.value(["Age groups are the same as used by World Bank for consistency and better understanding of our audience."])
                            )

    total_text = alt.layer(total_box,total_count)
    
    ### UNDERAGE BOX ###
    u18metric = base.mark_text(align="center",
                            baseline="top",
                            fill="#F16C8B",
                            fontSize=17,
                    ).encode(
                        x=alt.value(510),
                        y=alt.value(0),
                        text="count():Q"
                    ).transform_filter(
                        alt.FieldLTEPredicate(field="age",lte=17)
                    )
    u18title = alt.Chart().mark_text(align="left",
                              baseline="top",
                              fontSize=13,fill="#231F20").encode(
                                x=alt.value(410),
                                y=alt.value(-30),
                                text=alt.value(["Number of under-age","users (>18)"])
                                )
    
    u18rect = base.mark_rect(color="#E6E6E6",
                             cornerRadius=5).encode(
                                x=alt.value(400),x2=alt.value(550),
                                y=alt.value(-40),y2=alt.value(30),
                             )

    u18box = alt.layer(u18rect,u18title,u18metric)

    age_marital_chart = alt.layer(hist,text,u18box,total_text,worldbank_disclaimer)
    return age_marital_chart

# ----- CHARTS ----- #
# returns generic metric box
def get_default_metric_box(title=None,width=180,height=150):
    box = alt.Chart().mark_rect(
        width=width,
        height=height,
        color="#231F20",
    )
    if title:
        boxtitle = alt.Chart().mark_text(
            fill="#FFFCF9",
            x=-60,
            y=-60,
            align="left",
            fontSize=16,
            lineHeight=27,
            fontWeight=alt.FontWeight(100),
        ).encode(
            text=alt.value(title),
        )
        box = alt.layer(box,boxtitle)
    return box

def get_metrics_bar(base):
    ver = get_verified_users(base)
    eng = get_engaged_users(base)
    eng_ver = get_engaged_verified_users(base)
    reg = get_registered_users(base)
    return alt.vconcat(ver,eng,eng_ver,reg,spacing=0)

def get_verified_users(base):
    box = get_default_metric_box(title=["Number of","Verified Users"])
    text = base.mark_text(
        fill="#e7ee47",
        fontSize=30,
        fontWeight="bold",
        yOffset=10,
    ).transform_filter(
        "(datum.role == 5) & (datum.is_verifying_otp == 1) & (isValid(datum.deleted_at))"
    ).encode(
        text="count():Q"
    )
    chart = (box + text)
    return chart

def get_engaged_users(base):
    box = get_default_metric_box(title=["Number of Engaged","Users in Past 6 months"])
    text = base.mark_text(
        fill="#FFFCF9",
        fontSize=30,
        fontWeight="bold",
        yOffset=20,
    ).transform_filter(
        alt.FieldGTEPredicate(field="updated_at",gte=(pd.Timestamp.today()-pd.Timedelta(180,"days")).to_datetime64())
    ).transform_filter(
        "isValid(datum.updated_at)"
    ).encode(
        text="count():Q"
    )
    chart = (box + text)
    return chart

def get_engaged_verified_users(base):
    box = get_default_metric_box(title=["Engaged Users in","Number of Verified","Users (%)"],height=200)
    text = base.mark_text(
        fill="#FFFCF9",
        fontSize=30,
        fontWeight="bold",
        yOffset=20,
    ).transform_filter(
        "(datum.role == 5) & (datum.is_verifying_otp == 1) & (isValid(datum.deleted_at))"
    ).transform_filter(
        alt.FieldGTEPredicate(field="updated_at",gte=(pd.Timestamp.today()-pd.Timedelta(180,"days")).to_datetime64())
    ).transform_filter(
        "isValid(datum.updated_at)"
    ).encode(
        text="count():Q"
    )
    chart = (box + text)
    return chart

def get_registered_users(base):
    box = get_default_metric_box(title=["Number of","Registered Users"],height=200)
    text = base.mark_text(
        fill="#FFFCF9",
        fontSize=30,
        fontWeight="bold",
        yOffset=20,
    ).transform_filter(
        "isValid(datum.first_name) | isValid(datum.last_name) | isValid(datum.nickname)"
    ).encode(
        text="count():Q"
    )
    chart = (box + text)
    return chart