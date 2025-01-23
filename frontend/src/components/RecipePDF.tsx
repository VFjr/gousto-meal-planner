import { Document, Page, Text, View, StyleSheet, Image, Font } from '@react-pdf/renderer';
import Html from 'react-pdf-html';
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

// Register the Roboto font
Font.register({
    family: 'Inter',
    fonts: [
        {
            src: 'https://fonts.gstatic.com/s/inter/v12/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuLyeMZhrib2Bg-4.ttf',
            fontWeight: 100,
        },
        {
            src: 'https://fonts.gstatic.com/s/inter/v12/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuDyfMZhrib2Bg-4.ttf',
            fontWeight: 200,
        },
        {
            src: 'https://fonts.gstatic.com/s/inter/v12/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuOKfMZhrib2Bg-4.ttf',
            fontWeight: 300,
        },
        {
            src: 'https://fonts.gstatic.com/s/inter/v12/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuLyfMZhrib2Bg-4.ttf',
            fontWeight: 400,
        },
        {
            src: 'https://fonts.gstatic.com/s/inter/v12/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuI6fMZhrib2Bg-4.ttf',
            fontWeight: 500,
        },
        {
            src: 'https://fonts.gstatic.com/s/inter/v12/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuGKYMZhrib2Bg-4.ttf',
            fontWeight: 600,
        },
        {
            src: 'https://fonts.gstatic.com/s/inter/v12/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuFuYMZhrib2Bg-4.ttf',
            fontWeight: 700,
        },
        {
            src: 'https://fonts.gstatic.com/s/inter/v12/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuDyYMZhrib2Bg-4.ttf',
            fontWeight: 800,
        },
        {
            src: 'https://fonts.gstatic.com/s/inter/v12/UcCO3FwrK3iLTeHuS_fvQtMwCp50KnMw2boKoduKmMEVuBWYMZhrib2Bg-4.ttf',
            fontWeight: 900,
        },
    ],
});


const styles = StyleSheet.create({
    page: {
        padding: 15,
        fontFamily: 'Inter',
        flexDirection: 'column',
        flex: 1,
    },
    contentContainer: {
        flexDirection: 'row',
        gap: 10,
        marginBottom: 5,
        flexShrink: 0,
    },
    leftColumn: {
        width: '35%',
    },
    rightColumn: {
        width: '65%',
    },
    section: {
        flex: 1,
        flexDirection: 'column',
    },
    instructionsContent: {
        flex: 1,
        flexDirection: 'row',
        gap: 10,
    },
    instructionColumn: {
        flex: 1,
        flexDirection: 'column',
    },
    title: {
        fontSize: 18,
        marginBottom: 10,
        color: '#d32f2f',
        textAlign: 'center',
        fontWeight: 'bold',
    },
    sectionTitle: {
        fontSize: 12,
        marginBottom: 5,
        color: '#d32f2f',
        fontWeight: 'bold',
        borderBottomWidth: 1,
        borderBottomColor: '#d32f2f',
        borderBottomStyle: 'solid',
    },
    meta: {
        flexDirection: 'row',
        gap: 10,
        marginBottom: 10,
        color: '#666',
        fontSize: 9,
    },
    image: {
        width: '100%',
        height: 180,
        objectFit: 'cover',
        borderRadius: 5,
    },
    ingredientImage: {
        width: 20,
        height: 20,
        borderRadius: 8,
    },
    instructionImage: {
        position: 'absolute',
        width: 60,
        height: 100,
        objectFit: 'cover',
        borderRadius: 3,
    },
    instructionImageContainer: {
        width: 60,
        minWidth: 60,
        height: 100,
        overflow: 'hidden',
        position: 'relative',
    },
    ingredientsGrid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        gap: 5,
    },
    ingredientCard: {
        width: '32%',
        padding: 3,
        backgroundColor: '#f8f9fa',
        borderRadius: 3,
        marginBottom: 3,
        flexDirection: 'row',
        alignItems: 'center',
        gap: 3,
    },
    ingredient: {
        fontSize: 9,
        flex: 1,
    },
    instruction: {
        flex: 1,
        marginBottom: 5,
    },
    instructionContent: {
        flex: 1,
        flexDirection: 'row',
        gap: 5,
        alignItems: 'flex-start',
    },
    instructionTextContainer: {
        flex: 1,
        paddingLeft: 0,
        flexDirection: 'column',
        justifyContent: 'center',
    },
    instructionText: {
        fontSize: 8,
        marginBottom: 3,
    },
    // New styles for basic ingredients
    basicIngredientsContainer: {
        marginTop: 3,
        paddingTop: 3,
        borderTopWidth: 1,
        borderTopColor: '#f0f0f0',
        borderTopStyle: 'solid',
    },

    basicIngredientsGrid: {
        flexDirection: 'row',
        flexWrap: 'wrap',
        gap: 5,
    },
    basicIngredientItem: {
        backgroundColor: '#f8f9fa',
        padding: 3,
        borderRadius: 3,
        fontSize: 8,
    },
});

const instructionHtmlStylesheet = {
    p: {
        margin: 2,
    },
    '.text-purple': {
        color: 'purple',
    },
    '.text-danger': {
        color: 'red',
    },
};

function adjustSpaceInHtmlTags(html: string) {
    // https://github.com/danomatic/react-pdf-html/issues/100
    // Use a regular expression to find <strong> or <span> tags with a leading space after them and move the space before the tag
    return html.replace(/(<(strong|span)>)\s+/g, ' $1');
}

const RecipePDF: React.FC<RecipePDFProps> = ({ recipe, images, onBlobReady }) => {
    useEffect(() => {
        // Notify parent when component is mounted (blob is being prepared)
        onBlobReady?.();
    }, [onBlobReady]);

    if (!images) return null;

    const midPoint = Math.ceil(recipe.instruction_steps.length / 2);
    const leftColumnInstructions = recipe.instruction_steps.slice(0, midPoint);
    const rightColumnInstructions = recipe.instruction_steps.slice(midPoint);

    return (
        <Document>
            <Page size="A4" style={styles.page}>
                <Text style={styles.title}>{recipe.title}</Text>

                <View style={styles.contentContainer}>
                    <View style={styles.leftColumn}>
                        {images.main && (
                            <Image
                                style={styles.image}
                                src={images.main}
                            />
                        )}
                    </View>

                    <View style={styles.rightColumn}>
                        <Text style={styles.sectionTitle}>Ingredients</Text>
                        <View style={styles.ingredientsGrid}>
                            {recipe.ingredients.map((recipeIngredient) => (
                                <View key={recipeIngredient.ingredient.id} style={styles.ingredientCard}>
                                    {images.ingredients[recipeIngredient.ingredient.id] && (
                                        <Image
                                            style={styles.ingredientImage}
                                            src={images.ingredients[recipeIngredient.ingredient.id]}
                                        />
                                    )}
                                    <Text style={styles.ingredient}>
                                        {recipeIngredient.amount} {recipeIngredient.ingredient.name}
                                    </Text>
                                </View>
                            ))}
                        </View>

                        {/* Add basic ingredients section */}
                        {recipe.basic_ingredients && recipe.basic_ingredients.length > 0 && (
                            <View style={styles.basicIngredientsContainer}>
                                <View style={styles.basicIngredientsGrid}>
                                    {recipe.basic_ingredients.map((ingredient, index) => (
                                        <Text key={index} style={styles.basicIngredientItem}>
                                            {ingredient}
                                        </Text>
                                    ))}
                                </View>
                            </View>
                        )}
                    </View>
                </View>

                <View style={styles.section}>
                    <Text style={styles.sectionTitle}>Instructions</Text>
                    <View style={styles.instructionsContent}>
                        <View style={styles.instructionColumn}>
                            {leftColumnInstructions.map((step) => (
                                <View key={step.id} style={styles.instruction}>
                                    <View style={styles.instructionContent}>
                                        <View style={styles.instructionImageContainer}>
                                            {images.instructions[step.id] && (
                                                <Image
                                                    style={styles.instructionImage}
                                                    src={images.instructions[step.id]}
                                                />
                                            )}
                                        </View>
                                        <View style={styles.instructionTextContainer}>
                                            <Html
                                                stylesheet={instructionHtmlStylesheet}
                                                style={{ fontSize: 8 }}
                                            >
                                                {adjustSpaceInHtmlTags(step.text)}
                                            </Html>
                                        </View>
                                    </View>
                                </View>
                            ))}
                        </View>

                        <View style={styles.instructionColumn}>
                            {rightColumnInstructions.map((step) => (
                                <View key={step.id} style={styles.instruction}>
                                    <View style={styles.instructionContent}>
                                        <View style={styles.instructionImageContainer}>
                                            {step.order === 8 ? (
                                                images.main && (
                                                    <Image
                                                        style={styles.instructionImage}
                                                        src={images.main}
                                                    />
                                                )
                                            ) : (
                                                images.instructions[step.id] && (
                                                    <Image
                                                        style={styles.instructionImage}
                                                        src={images.instructions[step.id]}
                                                    />
                                                )
                                            )}
                                        </View>
                                        <View style={styles.instructionTextContainer}>
                                            <Html
                                                stylesheet={instructionHtmlStylesheet}
                                                style={{ fontSize: 8 }}
                                            >
                                                {adjustSpaceInHtmlTags(step.text)}
                                            </Html>
                                        </View>
                                    </View>
                                </View>
                            ))}
                        </View>
                    </View>
                </View>
            </Page>
        </Document>
    );
};

export { RecipePDF };
export type { ImageData, RecipePDFProps };
