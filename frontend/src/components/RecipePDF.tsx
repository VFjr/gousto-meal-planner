import { Document, Page, Text, View, StyleSheet, Image } from '@react-pdf/renderer';
import { Recipe } from '../types';
import { useEffect } from 'react';

interface ImageData {
    main: string | null;
    ingredients: { [key: number]: string };
    instructions: { [key: number]: string };
}
interface RecipePDFProps {
    recipe: Recipe;
    images: ImageData | null;
    onBlobReady?: () => void;
}

const styles = StyleSheet.create({
    page: {
        padding: 30,
    },
    title: {
        fontSize: 24,
        marginBottom: 10,
    },
    mainImage: {
        width: '100%',
        marginBottom: 20,
    },
    sectionTitle: {
        fontSize: 18,
        marginBottom: 10,
        marginTop: 20,
    },
    ingredientRow: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 10,
    },
    ingredientText: {
        flex: 1,
        marginRight: 10,
    },
    ingredientImage: {
        width: 30,
        height: 30,
        objectFit: 'contain',
    },
    instructionStep: {
        marginBottom: 10,
    },
    instructionImage: {
        width: '100%',
        height: 200,
        marginTop: 10,
        objectFit: 'contain',
    },
});

const RecipePDF: React.FC<RecipePDFProps> = ({ recipe, images, onBlobReady }) => {
    useEffect(() => {
        // Notify parent when component is mounted (blob is being prepared)
        onBlobReady?.();
    }, [onBlobReady]);

    if (!images) return null;

    console.log('PDF Images:', images.ingredients);  // Add this line to debug

    return (
        <Document>
            <Page size="A4" style={styles.page}>
                <View>
                    <Text style={styles.title}>{recipe.title}</Text>

                    {images.main && (
                        <Image src={images.main} style={styles.mainImage} />
                    )}

                    {recipe.ingredients?.length > 0 && (
                        <>
                            <Text style={styles.sectionTitle}>Ingredients:</Text>
                            {recipe.ingredients.map((recipeIngredient, index) => (
                                <View key={index} style={styles.ingredientRow}>
                                    <Text style={styles.ingredientText}>
                                        {recipeIngredient.amount} {recipeIngredient.ingredient.name}
                                    </Text>
                                    {images.ingredients[recipeIngredient.ingredient.id] && (
                                        <Image
                                            src={images.ingredients[recipeIngredient.ingredient.id]}
                                            style={styles.ingredientImage}
                                        />
                                    )}
                                </View>
                            ))}
                        </>
                    )}

                    {recipe.instruction_steps?.length > 0 && (
                        <>
                            <Text style={styles.sectionTitle}>Instructions:</Text>
                            {recipe.instruction_steps.map((step, index) => (
                                <View key={index} style={styles.instructionStep}>
                                    <Text>{step.order}. {step.text}</Text>
                                    {images.instructions[step.id] && (
                                        <Image
                                            src={images.instructions[step.id]}
                                            style={styles.instructionImage}
                                        />
                                    )}
                                </View>
                            ))}
                        </>
                    )}
                </View>
            </Page>
        </Document>
    );
};

export { RecipePDF };
export type { ImageData, RecipePDFProps };
