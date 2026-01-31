"""
PDF Generator for F.A.D. Army Lists
Generates professional army list PDFs with unit stat tables similar to OPR Army Forge
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image, KeepTogether
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from datetime import datetime
import os


class ArmyListPDFGenerator:
    """Generate professional PDF exports for army lists"""
    
    def __init__(self, army_list, units_with_quantities):
        self.army_list = army_list
        self.units_with_quantities = units_with_quantities
        self.buffer = BytesIO()
        self.pagesize = A4
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0d6efd'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#0d6efd'),
            spaceAfter=6,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Unit name style
        self.styles.add(ParagraphStyle(
            name='UnitName',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.black,
            spaceAfter=3,
            fontName='Helvetica-Bold'
        ))
        
        # Small text style
        self.styles.add(ParagraphStyle(
            name='SmallText',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.grey
        ))
    
    def generate(self):
        """Generate the PDF and return the buffer"""
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=self.pagesize,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=15*mm,
            bottomMargin=15*mm,
            title=f"FAD Army List - {self.army_list.name}"
        )
        
        # Build PDF content
        story = []
        story.extend(self._build_header())
        story.append(Spacer(1, 10*mm))
        story.extend(self._build_summary())
        story.append(Spacer(1, 8*mm))
        story.extend(self._build_units_section())
        story.append(Spacer(1, 10*mm))
        story.extend(self._build_footer())
        
        # Build PDF
        doc.build(story)
        self.buffer.seek(0)
        return self.buffer
    
    def _build_header(self):
        """Build PDF header with army list name and metadata"""
        elements = []
        
        # Title
        title = Paragraph(self.army_list.name, self.styles['CustomTitle'])
        elements.append(title)
        
        # Metadata
        faction_name = self.army_list.faction_obj.name if self.army_list.faction_obj else 'Custom Faction'
        metadata_text = f"""
        <para alignment="center">
            <b>Faction:</b> {faction_name} | 
            <b>Total Points:</b> {self.army_list.total_points} | 
            <b>Units:</b> {self.army_list.total_units}<br/>
            <font size="8" color="grey">Created by {self.army_list.owner.username} on {self.army_list.created_at.strftime('%Y-%m-%d')}</font>
        </para>
        """
        elements.append(Paragraph(metadata_text, self.styles['Normal']))
        
        # Description if present
        if self.army_list.description:
            elements.append(Spacer(1, 3*mm))
            desc_style = ParagraphStyle(
                name='Description',
                parent=self.styles['Normal'],
                fontSize=10,
                textColor=colors.grey,
                alignment=TA_JUSTIFY
            )
            elements.append(Paragraph(self.army_list.description, desc_style))
        
        # Horizontal line
        elements.append(Spacer(1, 3*mm))
        line_table = Table([['']], colWidths=[doc_width(self.pagesize)])
        line_table.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 2, colors.HexColor('#0d6efd')),
        ]))
        elements.append(line_table)
        
        return elements
    
    def _build_summary(self):
        """Build army composition summary table"""
        elements = []
        
        # Section header
        elements.append(Paragraph("Army Composition", self.styles['SectionHeader']))
        
        # Build summary data
        summary_data = [
            ['Unit Type', 'Quantity', 'Points Each', 'Total Points']
        ]
        
        for item in self.units_with_quantities:
            unit = item['unit']
            quantity = item['quantity']
            summary_data.append([
                unit.name,
                str(quantity),
                f"{unit.total_points}",
                f"{unit.total_points * quantity}"
            ])
        
        # Add total row
        summary_data.append([
            Paragraph('<b>TOTAL</b>', self.styles['Normal']),
            Paragraph(f'<b>{self.army_list.total_units}</b>', self.styles['Normal']),
            '',
            Paragraph(f'<b>{self.army_list.total_points}</b>', self.styles['Normal'])
        ])
        
        # Create table
        col_widths = [80*mm, 25*mm, 30*mm, 30*mm]
        summary_table = Table(summary_data, colWidths=col_widths)
        summary_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Data rows
            ('BACKGROUND', (0, 1), (-1, -2), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            
            # Total row
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e9ecef')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.black),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(summary_table)
        return elements
    
    def _build_units_section(self):
        """Build detailed unit stat cards"""
        elements = []
        
        elements.append(Paragraph("Unit Details", self.styles['SectionHeader']))
        elements.append(Spacer(1, 3*mm))
        
        for item in self.units_with_quantities:
            unit = item['unit']
            quantity = item['quantity']
            
            # Keep unit card together on same page
            unit_elements = []
            
            # Unit header
            unit_header_text = f"<b>{unit.name}</b> × {quantity}"
            unit_elements.append(Paragraph(unit_header_text, self.styles['UnitName']))
            
            # Unit stats table
            stats_table = self._build_unit_stats_table(unit)
            unit_elements.append(stats_table)
            
            # Equipment and traits
            equipment_text = self._build_equipment_text(unit)
            if equipment_text:
                unit_elements.append(Spacer(1, 2*mm))
                unit_elements.append(Paragraph(equipment_text, self.styles['Normal']))
            
            # Description if present
            if unit.description:
                unit_elements.append(Spacer(1, 2*mm))
                desc_para = Paragraph(f"<i>{unit.description}</i>", self.styles['SmallText'])
                unit_elements.append(desc_para)
            
            # Add spacing between units
            unit_elements.append(Spacer(1, 5*mm))
            
            # Keep together
            elements.append(KeepTogether(unit_elements))
        
        return elements
    
    def _build_unit_stats_table(self, unit):
        """Build stat table for a single unit"""
        # Prepare stats based on unit type
        if unit.unit_type == 'Squad':
            headers = ['Type', 'Quality', 'Resolve', 'Size', 'Armour', 'Points']
            values = [
                'Squad',
                unit.quality,
                unit.resolve,
                str(unit.squad_size),
                unit.armour.name if unit.armour else 'None',
                f"{unit.total_points}"
            ]
        elif unit.unit_type == 'Character':
            headers = ['Type', 'Quality', 'Resolve', 'Leadership', 'Armour', 'Points']
            values = [
                'Character',
                unit.quality,
                unit.resolve,
                unit.leadership_rating or 'Novice',
                unit.armour.name if unit.armour else 'None',
                f"{unit.total_points}"
            ]
        elif unit.unit_type == 'HeavyWeapon':
            headers = ['Type', 'Quality', 'Resolve', 'Crew', 'Armour', 'Points']
            values = [
                'Heavy Weapon',
                unit.quality,
                unit.resolve,
                str(unit.crew_count),
                unit.armour.name if unit.armour else 'None',
                f"{unit.total_points}"
            ]
        elif unit.unit_type == 'Sniper':
            headers = ['Type', 'Quality', 'Resolve', 'Armour', 'Points']
            values = [
                'Sniper',
                unit.quality,
                unit.resolve,
                unit.armour.name if unit.armour else 'None',
                f"{unit.total_points}"
            ]
        elif unit.unit_type == 'Psionic':
            headers = ['Type', 'Quality', 'Resolve', 'Aptitude', 'Strength', 'Points']
            values = [
                'Psionic',
                unit.quality,
                unit.resolve,
                unit.psionic_aptitude or 'Marginal',
                str(unit.psionic_strength or 0),
                f"{unit.total_points}"
            ]
        elif unit.unit_type == 'Vehicle':
            headers = ['Type', 'Quality', 'Movement', 'Armour F/S/R', 'Crew', 'Points']
            values = [
                unit.vehicle_type or 'Vehicle',
                unit.quality,
                unit.movement_type or 'Tracked',
                f"{unit.vehicle_armour_front}/{unit.vehicle_armour_side}/{unit.vehicle_armour_rear}",
                str(unit.crew_size),
                f"{unit.total_points}"
            ]
        else:
            headers = ['Type', 'Quality', 'Resolve', 'Points']
            values = ['Unit', unit.quality, unit.resolve, f"{unit.total_points}"]
        
        # Create table
        data = [headers, values]
        col_widths = [doc_width(self.pagesize) / len(headers)] * len(headers)
        
        table = Table(data, colWidths=col_widths)
        table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6c757d')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            
            # Data
            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#f8f9fa')),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, 1), 9),
            ('ALIGN', (0, 1), (-1, 1), 'CENTER'),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        return table
    
    def _build_equipment_text(self, unit):
        """Build equipment and traits description"""
        parts = []
        
        # Weapons
        weapon_list = []
        if unit.basic_weapon:
            weapon_list.append(f"<b>Primary:</b> {unit.basic_weapon.name}")
        if unit.secondary_weapon:
            weapon_list.append(f"<b>Secondary:</b> {unit.secondary_weapon.name}")
        if unit.heavy_weapon:
            weapon_list.append(f"<b>Heavy:</b> {unit.heavy_weapon.name}")
        
        if weapon_list:
            parts.append("<b>Weapons:</b> " + " | ".join(weapon_list))
        
        # Traits
        traits = unit.get_traits()
        if traits:
            trait_names = [trait.name for trait in traits]
            parts.append(f"<b>Traits:</b> {', '.join(trait_names)}")
        
        # Vehicle specific
        if unit.unit_type == 'Vehicle' and unit.carrying_capacity:
            parts.append(f"<b>Transport Capacity:</b> {unit.carrying_capacity} infantry")
        
        return "<br/>".join(parts) if parts else None
    
    def _build_footer(self):
        """Build PDF footer"""
        elements = []
        
        footer_text = f"""
        <para alignment="center" fontSize="8" color="grey">
            Generated by F.A.D. List Builder on {datetime.now().strftime('%Y-%m-%d %H:%M')}<br/>
            https://fad-helper.onrender.com
        </para>
        """
        elements.append(Paragraph(footer_text, self.styles['SmallText']))
        
        return elements


def doc_width(pagesize):
    """Calculate usable document width"""
    return pagesize[0] - 40*mm


def generate_army_list_pdf(army_list, units_with_quantities):
    """Main function to generate PDF for an army list"""
    generator = ArmyListPDFGenerator(army_list, units_with_quantities)
    return generator.generate()
