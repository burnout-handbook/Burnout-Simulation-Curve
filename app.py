from shiny import App, ui, render, reactive, Inputs, Outputs, Session
import numpy as np
import matplotlib.pyplot as plt
import os
import matplotlib.font_manager as fm

# 中英双语词典
lang_dict = {
    "zh": {
        "page_title": "学习动机/厌学关键期模拟计算",
        "language_select": "选择语言 / Select Language",
        "classes_question_num": "1.",
        "classes_question_text": "您个人/班级每周的平均学习课时有多少？（包括自习课；一课时=40/45分钟）",
        "classes_hint": "提示：请输入0-100之间的整数，超过100将自动按100处理",
        "gender_question_num": "2.",
        "gender_question_text": "您的性别是？",
        "gender_male": "男",
        "gender_female": "女",
        "gender_other": "为班级做计算、无性别",
        "motivation_question_num": "3. ",
        "motivation_question_text": "请输入您的初始学习动机值（1-4分）",
        "motivation_ref_method": "参考计算方法：",
        "motivation_step1": "1. 先完成以下3道自测题，每题选择对应选项；",
        "motivation_step2": "2. 计算3道题的平均分作为初始动机值填入上方输入框。(精确到0.1)",
        "motivation_self1": "问题1：您在学习时是否非常投入？",
        "motivation_self2": "问题2：您在上课时是否感到充满动力？",
        "motivation_self3": "问题3：您在做作业时是否感到充满动力？",
        "score_1": "1分 - 没有",
        "score_2": "2分 - 有一点",
        "score_3": "3分 - 还不错",
        "score_4": "4分 - 充满动力",
        "motivation_formula_title": "平均分计算公式：",
        "motivation_formula": "初始动机值 = （问题1得分 + 问题2得分 + 问题3得分） ÷ 3",
        "motivation_example": "例如：若3道题得分分别为3分、4分、3分，则初始动机值 = （3+4+3）÷3 ≈ 3.3分",
        "submit_btn": "计算评价结果",
        "reset_btn": "重新评价",
        "complete_all_hint": "请完成所有问题后再提交",
        "motivation_input_hint": "请根据以下参考问题和计算方法，输入您的初始学习动机值",
        "result_title": "您的评价结果",
        "motivation_start_point": "动机起始点: ",
        "chart_title": "学习动机趋势预测",
        "chart_xlabel": "周数",
        "chart_ylabel": "平均学习动机水平",
        "chart_legend_study_time": "{study_time}课时/周",
        "chart_legend_burnout": "厌学阈值",
        "chart_annotation_burnout": "第{week}周达到厌学阈值",
        "chart_region_burnout": "厌学区域",
        "chart_region_low": "低动机区域",
        "chart_region_high": "高动机区域",
        "gender_text_male": "男性",
        "gender_text_female": "女性",
        "gender_text_other": "整体"
    },
    "en": {
        "page_title": "Academic motivation/School Burnout Critical Week Simulation",
        "language_select": "Select Language / 选择语言",
        "classes_question_num": "1.",
        "classes_question_text": "What is your average weekly study hours (including self-study; 1 class hour = 40/45 minutes)?",
        "classes_hint": "Hint: Please enter an integer between 0-100; values over 100 will be treated as 100",
        "gender_question_num": "2.",
        "gender_question_text": "What is your gender?",
        "gender_male": "Male",
        "gender_female": "Female",
        "gender_other": "For class calculation (no gender)",
        "motivation_question_num": "3. ",
        "motivation_question_text": "Please enter your initial learning motivation score (1-4 points)",
        "motivation_ref_method": "Reference Calculation Method:",
        "motivation_step1": "1. First complete the following 3 self-assessment questions and select the corresponding option for each;",
        "motivation_step2": "2. Calculate the average score of the 3 questions and enter it as the initial motivation value above (accurate to 0.1).",
        "motivation_self1": "Question 1: Are you very engaged when studying?",
        "motivation_self2": "Question 2: Do you feel motivated in class?",
        "motivation_self3": "Question 3: Do you feel motivated when doing homework?",
        "score_1": "1 point - Not at all",
        "score_2": "2 points - Slightly",
        "score_3": "3 points - Moderately",
        "score_4": "4 points - Highly motivated",
        "motivation_formula_title": "Average Score Calculation Formula:",
        "motivation_formula": "Initial Motivation = (Score of Q1 + Score of Q2 + Score of Q3) ÷ 3",
        "motivation_example": "Example: If scores are 3, 4, 3, then Initial Motivation = (3+4+3) ÷3 ≈ 3.3 points",
        "submit_btn": "Calculate Evaluation Result",
        "reset_btn": "Re-evaluate",
        "complete_all_hint": "Please complete all questions before submitting",
        "motivation_input_hint": "Please enter your initial learning motivation based on the reference questions and calculation method below",
        "result_title": "Your Evaluation Result",
        "motivation_start_point": "Motivation Starting Point: ",
        "chart_title": "Learning Motivation Trend Prediction",
        "chart_xlabel": "Weeks",
        "chart_ylabel": "Average Learning Motivation Level",
        "chart_legend_study_time": "{study_time} Class Hours/Week",
        "chart_legend_burnout": "Burnout Threshold",
        "chart_annotation_burnout": "Reaches Burnout Threshold at Week {week}",
        "chart_region_burnout": "Burnout Zone",
        "chart_region_low": "Low Motivation Zone",
        "chart_region_high": "High Motivation Zone",
        "gender_text_male": "Male",
        "gender_text_female": "Female",
        "gender_text_other": "Overall"
    }
}

# UI组件定义
def question_block(question_num, question_text, lang):
    return ui.div(
        ui.h4(
            ui.span(
                question_num, 
                style="display: inline-block; background-color: #3498db; color: white; padding: 3px 8px; border-radius: 12px; margin-right: 8px;"
            ),
            question_text,
            style="margin-bottom: 15px; color: #34495e;"
        ),
        ui.input_radio_buttons(
            f"q{question_num.strip('. ')}",
            "",
            {
                "1": lang_dict[lang]["score_1"],
                "2": lang_dict[lang]["score_2"],
                "3": lang_dict[lang]["score_3"],
                "4": lang_dict[lang]["score_4"]
            },
            inline=True
        ),
        style="padding: 20px; border: 1px solid #ddd; border-radius: 10px; margin-bottom: 30px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);"
    )

def classes_question_block(lang):
    return ui.div(
        ui.h4(
            ui.span(
                lang_dict[lang]["classes_question_num"],
                style="display: inline-block; background-color: #3498db; color: white; padding: 3px 8px; border-radius: 12px; margin-right: 8px;"
            ),
            lang_dict[lang]["classes_question_text"],
            style="margin-bottom: 15px; color: #3498db; font-weight: bold;"
        ),
        ui.div(
            ui.input_numeric(
                "class_count",
                "",
                value=None,
                min=0,
                step=1
            ),
            ui.p(lang_dict[lang]["classes_hint"],
                style="font-size: 14px; color: #7f8c8d; margin-top: 5px;"),
        ),
        style="padding: 20px; border: 1px solid #ddd; border-radius: 10px; margin-bottom: 30px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);"
    )

def motivation_input_block(lang):
    return ui.div(
        ui.h4(
            ui.span(
                lang_dict[lang]["motivation_question_num"], 
                style="display: inline-block; background-color: #3498db; color: white; padding: 3px 8px; border-radius: 12px; margin-right: 8px;"
            ),
            lang_dict[lang]["motivation_question_text"],
            style="margin-bottom: 15px; color: #34495e;"
        ),
        ui.input_numeric(
            "initial_motivation",
            "",
            value=None,
            min=1,
            max=4,
            step=0.1
        ),
        ui.div(
            ui.p(lang_dict[lang]["motivation_ref_method"], style="font-weight: bold; margin: 15px 0 10px 0;"),
            ui.p(lang_dict[lang]["motivation_step1"], style="margin: 8px 0 0 15px;"),
            ui.p(lang_dict[lang]["motivation_step2"], style="margin: 5px 0 0 15px;"),
            
            ui.div(
                ui.p(lang_dict[lang]["motivation_self1"], style="font-weight: 500; margin: 15px 0 8px 0;"),
                ui.tags.ul(
                    ui.tags.li(lang_dict[lang]["score_1"]),
                    ui.tags.li(lang_dict[lang]["score_2"]),
                    ui.tags.li(lang_dict[lang]["score_3"]),
                    ui.tags.li(lang_dict[lang]["score_4"])
                ),
                style="margin-left: 15px;"
            ),
            
            ui.div(
                ui.p(lang_dict[lang]["motivation_self2"], style="font-weight: 500; margin: 15px 0 8px 0;"),
                ui.tags.ul(
                    ui.tags.li(lang_dict[lang]["score_1"]),
                    ui.tags.li(lang_dict[lang]["score_2"]),
                    ui.tags.li(lang_dict[lang]["score_3"]),
                    ui.tags.li(lang_dict[lang]["score_4"])
                ),
                style="margin-left: 15px;"
            ),
            
            ui.div(
                ui.p(lang_dict[lang]["motivation_self3"], style="font-weight: 500; margin: 15px 0 8px 0;"),
                ui.tags.ul(
                    ui.tags.li(lang_dict[lang]["score_1"]),
                    ui.tags.li(lang_dict[lang]["score_2"]),
                    ui.tags.li(lang_dict[lang]["score_3"]),
                    ui.tags.li(lang_dict[lang]["score_4"])
                ),
                style="margin-left: 15px;"
            ),
            
            ui.div(
                ui.p(lang_dict[lang]["motivation_formula_title"], style="font-weight: bold; margin: 15px 0 10px 0;"),
                ui.p(lang_dict[lang]["motivation_formula"], 
                     style="margin: 0 0 0 15px; padding: 10px; background-color: #f0f7ff; border-left: 3px solid #3498db;"),
                ui.p(lang_dict[lang]["motivation_example"], 
                     style="margin: 8px 0 0 15px; font-style: italic;")
            ),
            
            style="padding: 15px; background-color: #f8f9fa; border-radius: 8px; margin-top: 10px; font-size: 14px; color: #555; border: 1px solid #e9ecef;"
        ),
        style="padding: 20px; border: 1px solid #ddd; border-radius: 10px; margin-bottom: 30px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);"
    )

def gender_question_block(lang):
    return ui.div(
        ui.h4(
            ui.span(
                lang_dict[lang]["gender_question_num"], 
                style="display: inline-block; background-color: #3498db; color: white; padding: 3px 8px; border-radius: 12px; margin-right: 8px;"
            ),
            lang_dict[lang]["gender_question_text"],
            style="margin-bottom: 15px; color: #34495e;"
        ),
        ui.input_radio_buttons(
            "gender",
            "",
            {
                "male": lang_dict[lang]["gender_male"],
                "female": lang_dict[lang]["gender_female"],
                "other": lang_dict[lang]["gender_other"]
            },
            inline=True
        ),
        style="padding: 20px; border: 1px solid #ddd; border-radius: 10px; margin-bottom: 30px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);"
    )

def questions_ui1(lang):
    return ui.div(
        classes_question_block(lang),
        gender_question_block(lang),
        id="content_container1"
    )

def questions_ui2(lang):
    return ui.div(
        motivation_input_block(lang),
        ui.div(
            ui.input_action_button(
                "submit", 
                lang_dict[lang]["submit_btn"],
                style="background-color: #3498db; color: white; border: none; padding: 10px 20px; font-size: 16px; border-radius: 5px; cursor: pointer;"
            ),
            style="text-align: center; margin-bottom: 40px;"
        ),
        id="content_container2"
    )

def results_ui(lang):
    return ui.div(
        ui.div(
            ui.h3(lang_dict[lang]["result_title"], style="text-align: center; margin-bottom: 20px; color: #2c3e50;"),
            ui.hr(style="margin-bottom: 30px;"),
            
            ui.div(
                ui.span(lang_dict[lang]["motivation_start_point"], style="font-size: 20px;"),
                ui.span(ui.output_text("avg_score"), style="font-size: 36px; font-weight: bold; color: #3498db;"),
                style="text-align: center; margin-bottom: 30px;"
            ),
            
            ui.div(
                ui.h4(lang_dict[lang]["chart_title"], style="text-align: center; margin: 20px 0;"),
                ui.output_plot("motivation_agent", width="100%", height="500px"),
                style="margin: 20px 0; padding: 10px; border: 1px solid #ddd; border-radius: 8px;"
            ),
            
            ui.div(
                ui.input_action_button(
                    "reset", 
                    lang_dict[lang]["reset_btn"],
                    style="background-color: #95a5a6; color: white; border: none; padding: 8px 16px; font-size: 14px; border-radius: 5px; cursor: pointer; margin-top: 30px;"
                ),
                style="text-align: center;"
            ),
            
            style="padding: 30px; border: 1px solid #ddd; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.07);"
        ),
        id="result_container"
    )

# 主UI
app_ui = ui.page_fluid(
    ui.div(
        ui.input_radio_buttons(
            "lang",
            lang_dict["zh"]["language_select"],
            choices={"zh": "中文 (Chinese)", "en": "英文 (English)"},
            selected="zh",
            inline=True
        ),
        style="text-align: center; margin-bottom: 30px; font-size: 16px;"
    ),
    
    ui.h2(ui.output_text("page_title"), style="text-align: center; margin-bottom: 30px; color: #2c3e50;"),
    ui.div(id="dynamic_content"),
    style="max-width: 900px; margin: 0 auto; padding: 20px;"
)

# 服务器逻辑
def server(input: Inputs, output: Outputs, session: Session):
    submitted = reactive.Value(False)
    
    # 修复：在服务器内部定义反应式语言变量，确保在反应式上下文中
    @reactive.calc
    def current_lang():
        return input.lang()

    @output
    @render.text
    def page_title():
        return lang_dict[current_lang()]["page_title"]

    # 监听语言变化，更新UI
    @reactive.Effect
    def _update_ui():
        # 移除所有旧内容
        ui.remove_ui(selector="#dynamic_content *")
        ui.remove_ui(selector="#result_container")
        
        # 根据提交状态插入对应UI
        if not submitted():
            ui.insert_ui(
                ui.div(
                    questions_ui1(current_lang()),
                    ui.p(lang_dict[current_lang()]["motivation_input_hint"], 
                         style="text-align: center; color: #7f8c8d; margin-bottom: 40px; font-size: 18px;"),
                    questions_ui2(current_lang())
                ),
                selector="#dynamic_content"
            )
        else:
            ui.insert_ui(results_ui(current_lang()), selector="#dynamic_content")

    # 提交按钮逻辑
    @reactive.Effect
    @reactive.event(input.submit)
    def _submit():
        if (input.class_count() is not None and 
            input.gender() and 
            input.initial_motivation() is not None):
            submitted.set(True)
            ui.remove_ui(selector="#content_container1")
            ui.remove_ui(selector="#content_container2")
            ui.insert_ui(results_ui(current_lang()), selector="#dynamic_content")
        else:
            ui.notification_show(lang_dict[current_lang()]["complete_all_hint"], type="warning")

    # 重置按钮逻辑
    @reactive.Effect
    @reactive.event(input.reset)
    def _reset():
        submitted.set(False)
        ui.remove_ui(selector="#result_container")
        ui.insert_ui(
            ui.div(
                questions_ui1(current_lang()),
                ui.p(lang_dict[current_lang()]["motivation_input_hint"], 
                     style="text-align: center; color: #7f8c8d; margin-bottom: 40px; font-size: 18px;"),
                questions_ui2(current_lang())
            ),
            selector="#dynamic_content"
        )

    @output
    @render.text
    def avg_score():
        return round(input.initial_motivation(), 1)

    @output
    @render.plot
    def motivation_agent():
        # 字体配置
        plt.rcParams["axes.unicode_minus"] = False
        font_prop = None
        
        if current_lang() == "zh":
            # 中文：尝试加载SimHei字体
            try:
                font_path = os.path.join(os.path.dirname(__file__), "fonts", "simhei.ttf")
                if os.path.exists(font_path):
                    font_prop = fm.FontProperties(fname=font_path)
                    plt.rcParams["font.family"] = font_prop.get_name()
                else:
                    plt.rcParams["font.family"] = ["WenQuanYi Micro Hei", "Heiti TC", "sans-serif"]
            except:
                plt.rcParams["font.family"] = ["WenQuanYi Micro Hei", "Heiti TC", "sans-serif"]
        else:
            # 英文：使用默认字体
            plt.rcParams["font.family"] = ["Arial", "sans-serif"]

        # 模拟数据计算
        num_students = 1000
        weeks = 70
        study_time = min(100, input.class_count())
        burnout_threshold = 1.0
        
        # 性别差异系数
        genderdif = 0.0043 if input.gender() == "male" else 0.0051 if input.gender() == "female" else 0.0047
        gender_text = (lang_dict[current_lang()]["gender_text_male"] if input.gender() == "male" 
                      else lang_dict[current_lang()]["gender_text_female"] if input.gender() == "female" 
                      else lang_dict[current_lang()]["gender_text_other"])

        # 初始化动机
        base_motivation = input.initial_motivation()
        initial_motivations = np.random.normal(base_motivation, 0.5, num_students)
        initial_motivations = np.clip(initial_motivations, 1, 5)

        # 其他参数初始化
        learning_efficiencies = np.clip(np.random.normal(0.5, 0.1, num_students), 0, 1)
        stress_resistances = np.clip(np.random.normal(0.5, 0.1, num_students), 0, 1)

        # 结果存储
        motivation_history = np.zeros((weeks, num_students))
        burnout_history = np.zeros((weeks, num_students), dtype=bool)
        burnout_weeks = np.full(num_students, np.nan)

        # 每周动机变化模拟
        for week in range(weeks):
            for student in range(num_students):
                if week > 0 and burnout_history[week-1, student]:
                    motivation_history[week, student] = motivation_history[week-1, student]
                    burnout_history[week, student] = True
                    continue

                actual_study_time = study_time
                prev_motivation = initial_motivations[student] if week == 0 else motivation_history[week-1, student]

                # 动机衰减计算
                base_decay = genderdif * actual_study_time
                efficiency_factor = 1 - learning_efficiencies[student] * 0.5
                resistance_factor = 1 - stress_resistances[student] * 0.5
                motivation_decay = base_decay * efficiency_factor * resistance_factor

                # 随机波动
                random_fluctuation = np.random.normal(0, 0.08)

                # 更新动机
                current_motivation = max(0, prev_motivation - motivation_decay + random_fluctuation)
                motivation_history[week, student] = current_motivation

                # 检查厌学
                if current_motivation <= burnout_threshold:
                    burnout_history[week, student] = True
                    if np.isnan(burnout_weeks[student]):
                        burnout_weeks[student] = week + 1

        # 计算平均动机
        avg_motivations = np.mean(motivation_history, axis=1)

        # 绘制图表
        plt.figure(figsize=(10, 6))

        # 平均动机曲线
        plt.plot(
            range(1, weeks+1), 
            avg_motivations, 
            '-', linewidth=2.5, 
            color='blue', 
            label=lang_dict[current_lang()]["chart_legend_study_time"].format(study_time=study_time)
        )

        # 标注与厌学阈值的交点
        cross_point = None
        for week_idx in range(1, weeks):
            if (avg_motivations[week_idx-1] >= burnout_threshold and 
                avg_motivations[week_idx] <= burnout_threshold):
                cross_point = (week_idx + 1, burnout_threshold)
                break
        if cross_point:
            plt.scatter(
                cross_point[0], cross_point[1], 
                color='red', s=100, 
                edgecolor='black', linewidth=1.5, zorder=5
            )
            plt.annotate(
                lang_dict[current_lang()]["chart_annotation_burnout"].format(week=cross_point[0]), 
                xy=cross_point, xytext=(5, 10), textcoords='offset points',
                fontsize=10, 
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec='red', alpha=0.8),
                fontproperties=font_prop if current_lang() == "zh" else None
            )

        # 厌学阈值线
        plt.axhline(
            y=burnout_threshold, 
            color='r', linestyle='--', linewidth=1.5, 
            label=lang_dict[current_lang()]["chart_legend_burnout"]
        )

        # 动机区域背景色
        plt.fill_between(
            range(1, weeks+1), 0, 1.0, 
            color='red', alpha=0.1, 
            label=lang_dict[current_lang()]["chart_region_burnout"]
        )
        plt.fill_between(
            range(1, weeks+1), 1.0, 2.5, 
            color='orange', alpha=0.1, 
            label=lang_dict[current_lang()]["chart_region_low"]
        )
        plt.fill_between(
            range(1, weeks+1), 2.5, 5.0, 
            color='green', alpha=0.1, 
            label=lang_dict[current_lang()]["chart_region_high"]
        )

        # 图表属性
        plt.title(
            f'{gender_text} {lang_dict[current_lang()]["chart_title"]}',
            fontproperties=font_prop if current_lang() == "zh" else None,
            fontsize=14
        )
        plt.xlabel(
            lang_dict[current_lang()]["chart_xlabel"],
            fontproperties=font_prop if current_lang() == "zh" else None,
            fontsize=12
        )
        plt.ylabel(
            lang_dict[current_lang()]["chart_ylabel"],
            fontproperties=font_prop if current_lang() == "zh" else None,
            fontsize=12
        )
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.xlim(1, weeks)
        plt.ylim(0, 5)
        plt.legend(prop=font_prop if current_lang() == "zh" else None)
        plt.tight_layout()

        return plt.gcf()

app = App(app_ui, server)
