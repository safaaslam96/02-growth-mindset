import streamlit as st
import pandas as pd
from io import BytesIO

# Optional plotly import
try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

st.set_page_config(page_title="🧹 File Converter & Cleaner", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom right, #003333, #001a1a);
        color: #f2f2f2;
        font-family: 'Segoe UI', sans-serif;
        animation: fadeIn 1.2s ease-in-out;
    }
    @keyframes fadeIn {
        0% {opacity: 0;}
        100% {opacity: 1;}
    }
    .main-title {
        color: #E0FFFF;
        text-align: center;
        font-size: 2.6em;
        margin-top: 1rem;
    }
    .stButton button {
        background: linear-gradient(to right, #00CED1, #20B2AA);
        color: #002B2B;
        border: none;
        border-radius: 10px;
        padding: 0.6em 1.3em;
        font-weight: bold;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        transition: 0.3s ease;
    }
    .stButton button:hover {
        background: linear-gradient(to right, #40E0D0, #48D1CC);
        transform: scale(1.05);
    }
    .stRadio > div, .stCheckbox > div {
        background-color: rgba(255, 255, 255, 0.07);
        border-radius: 10px;
        padding: 10px;
    }
    </style>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🏠 Home", "📁 Convert Files", "ℹ️ About"])

with tab1:
    st.markdown('<h1 class="main-title">🧹 File Converter & Cleaner</h1>', unsafe_allow_html=True)
    st.markdown("### Upload CSV/Excel files, clean data, visualize charts, and download in CSV, Excel, or PDF format.")

with tab2:
    st.markdown('<h1 class="main-title">📤 Upload & Process Files</h1>', unsafe_allow_html=True)

    files = st.file_uploader("Upload CSV or Excel files", type=["csv", "xlsx"], accept_multiple_files=True)

    if files:
        for file in files:
            ext = file.name.split(".")[-1]
            df = pd.read_csv(file) if ext == "csv" else pd.read_excel(file)

            st.subheader(f"📄 Preview: {file.name}")
            st.dataframe(df.head())

            if st.checkbox(f"🧼 Fill Missing Values - {file.name}"):
                df.fillna(df.select_dtypes(include="number").mean(), inplace=True)
                st.success("✅ Missing values filled!")
                st.dataframe(df.head())

                selected_columns = st.multiselect(f"🔍 Select Columns - {file.name}", df.columns, default=df.columns)
                df = df[selected_columns]
                st.dataframe(df.head())
                 
                st.success(f"✅ Plotly installed: {PLOTLY_AVAILABLE}")


                if PLOTLY_AVAILABLE and st.checkbox(f"📊 Show Animated Chart - {file.name}") and not df.select_dtypes(include="number").empty:
                    num_df = df.select_dtypes(include="number")
                    fig = px.bar(num_df.head(10), barmode='group', title='📈 Animated Bar Chart')
                    st.plotly_chart(fig, use_container_width=True)
                elif not PLOTLY_AVAILABLE:
                    st.warning("⚠️ Plotly is not installed. Chart visualization is unavailable.")

                format_choice = st.radio(f"💾 Convert {file.name} to:", ["CSV", "Excel", "PDF"], key=file.name)

                if st.button(f"⬇️ Download {file.name} as {format_choice}"):
                    output = BytesIO()
                    new_name = file.name.rsplit(".", 1)[0] + "." + format_choice.lower()

                    if format_choice == "CSV":
                        df.to_csv(output, index=False)
                        mime = "text/csv"

                    elif format_choice == "Excel":
                        try:
                            import openpyxl
                            df.to_excel(output, index=False)
                            mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        except ImportError:
                            st.error("❌ Excel export requires 'openpyxl'. Please install it.")
                            continue

                    else:  # PDF using reportlab
                        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
                        from reportlab.lib import colors
                        from reportlab.lib.pagesizes import A4

                        pdf = BytesIO()
                        doc = SimpleDocTemplate(pdf, pagesize=A4)
                        data = [list(df.columns)] + df.head(20).values.tolist()

                        table = Table(data)
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.teal),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, -1), 8),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                        ]))

                        doc.build([table])
                        pdf.seek(0)
                        output.write(pdf.read())
                        mime = "application/pdf"

                    output.seek(0)
                    st.download_button(
                        label=f"📥 Download {format_choice}",
                        file_name=new_name,
                        data=output,
                        mime=mime
                    )
                    st.success("🎉 File ready for download!")

with tab3:
    st.markdown('<h1 class="main-title">ℹ️ About This App</h1>', unsafe_allow_html=True)
    st.markdown("""
        This **Streamlit-based tool** lets you:
        - 📁 Upload and preview CSV or Excel files  
        - 🧼 Clean missing values and filter columns  
        - 📊 Visualize data with animated bar charts  
        - 💾 Download results as **CSV, Excel, or PDF**  
    """)
