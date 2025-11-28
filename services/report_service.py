from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
from models import Person, Video, VideoAppearance
from services.search_service import get_person_statistics, get_all_persons_statistics
from utils import format_time
import os

def generate_video_report_pdf(video_id, output_path):
    video = Video.get_by_id(video_id)
    if not video:
        return None
    
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph("Reporte de Análisis de Video", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph(f"<b>Nombre del archivo:</b> {video['original_filename']}", styles['Normal']))
    story.append(Paragraph(f"<b>Fecha de subida:</b> {video['uploaded_at']}", styles['Normal']))
    
    if video['duration']:
        story.append(Paragraph(f"<b>Duración:</b> {format_time(video['duration'])}", styles['Normal']))
    
    story.append(Paragraph(f"<b>Estado:</b> {'Procesado' if video['processed'] else 'Sin procesar'}", styles['Normal']))
    
    if video['processed_at']:
        story.append(Paragraph(f"<b>Fecha de procesamiento:</b> {video['processed_at']}", styles['Normal']))
    
    story.append(Spacer(1, 0.3*inch))
    
    if video['processed']:
        appearances = VideoAppearance.get_by_video(video_id)
        
        if appearances:
            story.append(Paragraph("<b>Personas Detectadas</b>", styles['Heading2']))
            story.append(Spacer(1, 0.1*inch))
            
            person_data = {}
            for app in appearances:
                person_name = app['person_name']
                if person_name not in person_data:
                    person_data[person_name] = []
                person_data[person_name].append({
                    'start': app['start_time'],
                    'end': app['end_time'],
                    'duration': app['end_time'] - app['start_time']
                })
            
            for person_name, segments in person_data.items():
                total_time = sum(s['duration'] for s in segments)
                
                story.append(Paragraph(f"<b>{person_name}</b>", styles['Heading3']))
                story.append(Paragraph(f"Apariciones: {len(segments)}", styles['Normal']))
                story.append(Paragraph(f"Tiempo total en pantalla: {format_time(total_time)}", styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
                
                table_data = [['#', 'Inicio', 'Fin', 'Duración']]
                for idx, seg in enumerate(segments, 1):
                    table_data.append([
                        str(idx),
                        format_time(seg['start']),
                        format_time(seg['end']),
                        format_time(seg['duration'])
                    ])
                
                table = Table(table_data, colWidths=[0.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(table)
                story.append(Spacer(1, 0.2*inch))
        else:
            story.append(Paragraph("No se detectaron personas en este video.", styles['Normal']))
    
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(f"<i>Reporte generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</i>", styles['Normal']))
    
    doc.build(story)
    return output_path

def generate_person_report_pdf(person_id, output_path):
    stats = get_person_statistics(person_id)
    if not stats:
        return None
    
    from services.search_service import search_videos_by_person
    video_data = search_videos_by_person(person_id)
    
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph(f"Reporte de Apariciones: {stats['person_name']}", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("<b>Estadísticas Generales</b>", styles['Heading2']))
    story.append(Paragraph(f"Total de videos donde aparece: <b>{stats['total_videos']}</b>", styles['Normal']))
    story.append(Paragraph(f"Total de apariciones: <b>{stats['total_appearances']}</b>", styles['Normal']))
    story.append(Paragraph(f"Tiempo total en pantalla: <b>{stats['total_screen_time_formatted']}</b>", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    if video_data['videos']:
        story.append(Paragraph("<b>Detalle por Video</b>", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        
        for video in video_data['videos']:
            story.append(Paragraph(f"<b>{video['filename']}</b>", styles['Heading3']))
            story.append(Paragraph(f"Apariciones: {video['total_appearances']}", styles['Normal']))
            story.append(Paragraph(f"Tiempo en pantalla: {video['total_duration_formatted']}", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
            
            table_data = [['#', 'Inicio', 'Fin', 'Duración']]
            for idx, app in enumerate(video['appearances'], 1):
                table_data.append([
                    str(idx),
                    app['start_formatted'],
                    app['end_formatted'],
                    format_time(app['duration'])
                ])
            
            table = Table(table_data, colWidths=[0.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            story.append(Spacer(1, 0.2*inch))
    
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(f"<i>Reporte generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</i>", styles['Normal']))
    
    doc.build(story)
    return output_path

def generate_global_statistics_pdf(output_path):
    all_stats = get_all_persons_statistics()
    
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    story.append(Paragraph("Reporte Global de Estadísticas", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    videos = Video.get_all()
    processed_videos = [v for v in videos if v['processed']]
    
    story.append(Paragraph(f"<b>Total de videos:</b> {len(videos)}", styles['Normal']))
    story.append(Paragraph(f"<b>Videos procesados:</b> {len(processed_videos)}", styles['Normal']))
    story.append(Paragraph(f"<b>Personas registradas:</b> {len(all_stats)}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    if all_stats:
        story.append(Paragraph("<b>Ranking de Apariciones</b>", styles['Heading2']))
        story.append(Spacer(1, 0.1*inch))
        
        table_data = [['#', 'Persona', 'Videos', 'Apariciones', 'Tiempo Total']]
        for idx, stat in enumerate(all_stats, 1):
            table_data.append([
                str(idx),
                stat['person_name'],
                str(stat['total_videos']),
                str(stat['total_appearances']),
                stat['total_screen_time_formatted']
            ])
        
        table = Table(table_data, colWidths=[0.5*inch, 2*inch, 1*inch, 1.2*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        
        story.append(table)
    
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(f"<i>Reporte generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</i>", styles['Normal']))
    
    doc.build(story)
    return output_path
