import streamlit as st
import pandas as pd

# 1. إعدادات الصفحة بتصميم احترافي
st.set_page_config(
    page_title="نظام إدارة الموردين",
    page_icon="📦",
    layout="wide"
)

# إضافة تنسيقات CSS لتحسين المظهر العربي
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Cairo', sans-serif;
        direction: RTL;
        text-align: right;
    }
    .stDataFrame {
        direction: RTL;
    }
    </style>
    """, unsafe_allow_html=True) # لاحظ التغيير هنا من name إلى html

# 2. وظيفة قراءة وتحويل البيانات
def load_data(file):
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        return df
    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
        return None

# 3. واجهة التطبيق
st.title("🚀 نظام إدارة قاعدة بيانات الموردين")
st.markdown("---")

# منطقة رفع الملفات
with st.container():
    uploaded_file = st.file_uploader("قم برفع ملف الموردين (Excel أو CSV) لتحويله داخل التطبيق", type=['xlsx', 'csv'])

if uploaded_file is not None:
    data = load_data(uploaded_file)
    
    if data is not None:
        st.success("✅ تم تحميل وتحويل القائمة بنجاح!")
        
        # تقسيم الواجهة لثلاثة أعمدة للبحث والفلترة
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search = st.text_input("🔍 ابحث في كافة البيانات (اسم، هاتف، منتج...):")
        
        # تنفيذ عملية البحث
        if search:
            mask = data.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)
            display_df = data[mask]
        else:
            display_df = data

        # عرض النتائج في جدول تفاعلي
        st.markdown(f"### إجمالي الموردين المتاحين: `{len(display_df)}`")
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # خيارات التصدير
        st.markdown("---")
        st.download_button(
            label="📥 تحميل القائمة الحالية (CSV)",
            data=display_df.to_csv(index=False).encode('utf-8-sig'),
            file_name='suppliers_export.csv',
            mime='text/csv',
        )
else:
    # رسالة ترحيبية وتعليمات عند عدم وجود ملف
    st.info("💡 للبدء، يرجى سحب وإفلات ملف الموردين الخاص بك هنا.")
    with st.expander("ℹ️ تعليمات الاستخدام"):
        st.write("""
        1. تأكد من أن ملف Excel يحتوي على رؤوس أعمدة واضحة.
        2. يمكنك البحث عن أي مورد بمجرد كتابة جزء من اسمه في خانة البحث.
        3. التطبيق يعمل كلياً في المتصفح ولا يتم حفظ ملفاتك على خوادم خارجية لضمان الخصوصية.
        """)
