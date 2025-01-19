import { Document, Page, Text, View, StyleSheet, Image, Font } from '@react-pdf/renderer';
import Html from 'react-pdf-html';
import { Recipe } from '../types';

interface RecipePDFProps {
    recipe: Recipe;
}

const RecipePDF: React.FC<RecipePDFProps> = ({ recipe }) => {
    return (
        <Document>
            <Page size="A4">
                <View>
                    <Text>{recipe.title}</Text>
                </View>
            </Page>
        </Document>
    );
};

export default RecipePDF;