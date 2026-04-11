import streamlit as st
import pandas as pd
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="نظام إدارة الموردين", layout="wide")

# تخصيص المظهر باللغة العربية
st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #10B981; color: white; }
    th { text-align: right !important; }
    td { text-align: right !important; }
    </style>
    """, unsafe_allow_name=True)

# بيانات افتراضية للبدء (يمكن استبدالها بملف Excel لاحقاً)
if 'supplier_data' not in st.session_state:
    st.session_state.supplier_data = pd.DataFrame([
        {
            "اسم المورد": "شركة الأمل للمعدات",
            "الفئة": "ميكانيك",
            "الشخص المسؤول": "أحمد محمد",
            "رقم الهاتف": "0550123456",
            "تاريخ انتهاء السجل": "2024-12-31",
            "الحالة": "معتمد"
        },
        {
            "اسم المورد": "مؤسسة الدرع الواقي",
            "الفئة": "أدوات حماية PPE",
            "الشخص المسؤول": "ياسين كريم",
            "رقم الهاتف": "0661987654",
            "تاريخ انتهاء السجل": "2023-05-20",
            "الحالة": "قيد المراجعة"
        }
    ])

# العنوان الرئيسي
st.title("📂 قاعدة بيانات الموردين المركزية")
st.subheader("تسهيل الوصول للبيانات وإدارة السجلات")

# القائمة الجانبية لإضافة مورد جديد
with st.sidebar:
    st.header("➕ إضافة مورد جديد")
    with st.form("add_supplier_form"):
        new_name = st.text_input("اسم الشركة/المورد")
        new_cat = st.selectbox("الفئة", ["ميكانيك", "أدوات حماية PPE", "مواد استهلاكية", "خدمات عامة", "قطع غيار"])
        new_contact = st.text_input("اسم الشخص المسؤول")
        new_phone = st.text_input("رقم الهاتف")
        new_expiry = st.date_input("تاريخ انتهاء السجل التجاري")
        new_status = st.selectbox("الحالة", ["معتمد", "قيد المراجعة", "غير معتمد"])
        
        submit_button = st.form_submit_button("حفظ المورد")
        
        if submit_button:
            new_row = {
                "اسم المورد": new_name,
                "الفئة": new_cat,
                "الشخص المسؤول": new_contact,
                "رقم الهاتف": new_phone,
                "تاريخ انتهاء السجل": str(new_expiry),
                "الحالة": new_status
            }
            st.session_state.supplier_data = pd.concat([st.session_state.supplier_data, pd.DataFrame([new_row])], ignore_index=True)
            st.success("تمت إضافة المورد بنجاح!")

# الجزء الرئيسي: البحث والعرض
col1, col2 = st.columns([2, 1])

with col1:
    search_query = st.text_input("🔍 ابحث عن مورد (بالاسم أو الفئة):")

# فلترة البيانات بناءً على البحث
df = st.session_state.supplier_data
if search_query:
    df = df[df['اسم المورد'].str.contains(search_query) | df['الفئة'].str.contains(search_query)]

# عرض الجدول بتنسيق لوني بسيط
def color_status(val):
    color = 'white'
    if val == 'معتمد': color = '#d4edda' # أخضر فاتح
    elif val == 'قيد المراجعة': color = '#fff3cd' # أصفر فاتح
    elif val == 'غير معتمد': color = '#f8d7da' # أحمر فاتح
    return f'background-color: {color}'

st.write(f"عدد الموردين المسجلين: {len(df)}")
st.table(df.style.applymap(color_status, subset=['الحالة']))

# ميزة تصدير البيانات
st.download_button(
    label="📥 تحميل قاعدة البيانات كـ Excel (CSV)",
    data=df.to_csv(index=False).encode('utf-8-sig'),
    file_name='suppliers_database.csv',
    mime='text/csv',
)

# ملاحظة إرشادية في الأسفل
st.info("نصيحة: يمكنك استخدام خيار 'إضافة مورد' من القائمة الجانبية لتحديث القاعدة فورياً.")
