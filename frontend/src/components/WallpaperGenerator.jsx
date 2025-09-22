import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Loader2, Download, RefreshCw, Smartphone } from 'lucide-react';
import PhonePreview from './PhonePreview';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API = `${API_BASE}/api`;

const WallpaperGenerator = () => {
  const [prompt, setPrompt] = useState('');
  const [style, setStyle] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedImage, setGeneratedImage] = useState(null);
  const [error, setError] = useState(null);

  const styles = [
    'Abstract',
    'Minimalist',
    'Nature',
    'Cyberpunk',
    'Watercolor',
    'Oil Painting',
    'Digital Art',
    'Photography',
    'Anime',
    'Geometric',
    'Gradient',
    'Neon'
  ];

  const generateWallpaper = async () => {
    if (!prompt.trim()) {
      setError('Please enter a prompt');
      return;
    }

    setIsGenerating(true);
    setError(null);

    try {
      const response = await axios.post(`${API}/generate-wallpaper`, {
        prompt: prompt.trim(),
        style: style,
        aspect_ratio: '9:16'
      });

      if (response.data.success) {
        setGeneratedImage(response.data.image_url);
      } else {
        setError(response.data.error || 'Failed to generate wallpaper');
      }
    } catch (err) {
      console.error('Error generating wallpaper:', err);
      setError('Failed to generate wallpaper. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const downloadWallpaper = () => {
    if (generatedImage) {
      const link = document.createElement('a');
      link.href = generatedImage;
      link.download = `wallpaper-${Date.now()}.jpg`;
      link.target = '_blank';
      link.click();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 p-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">
            AI Phone Wallpaper Generator
          </h1>
          <p className="text-gray-600">Create stunning phone wallpapers with AI</p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Generator Panel */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Smartphone className="w-5 h-5" />
                  Generate Wallpaper
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Describe your wallpaper
                  </label>
                  <Textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="e.g., Serene mountain landscape at sunset with purple sky, mystical forest with glowing fireflies, abstract geometric patterns..."
                    rows={3}
                    className="w-full"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    Style (optional)
                  </label>
                  <Select value={style} onValueChange={setStyle}>
                    <SelectTrigger>
                      <SelectValue placeholder="Choose a style" />
                    </SelectTrigger>
                    <SelectContent>
                      {styles.map((styleOption) => (
                        <SelectItem key={styleOption} value={styleOption.toLowerCase()}>
                          {styleOption}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {error && (
                  <div className="p-3 text-sm text-red-600 bg-red-50 rounded-md border border-red-200">
                    {error}
                  </div>
                )}

                <Button
                  onClick={generateWallpaper}
                  disabled={isGenerating}
                  className="w-full"
                  size="lg"
                >
                  {isGenerating ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    'Generate Wallpaper'
                  )}
                </Button>
              </CardContent>
            </Card>

            {/* Quick Prompts */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Prompts</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {[
                    'Neon cityscape at night',
                    'Peaceful mountain lake',
                    'Abstract rainbow waves',
                    'Cosmic galaxy spiral',
                    'Minimalist sunset',
                    'Cherry blossom spring'
                  ].map((quickPrompt) => (
                    <Badge
                      key={quickPrompt}
                      variant="secondary"
                      className="cursor-pointer hover:bg-purple-100"
                      onClick={() => setPrompt(quickPrompt)}
                    >
                      {quickPrompt}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Preview Panel */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Preview</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex justify-center">
                  <PhonePreview
                    imageUrl={generatedImage}
                    isLoading={isGenerating}
                  />
                </div>

                {generatedImage && (
                  <div className="mt-6 flex flex-col sm:flex-row gap-3">
                    <Button
                      onClick={downloadWallpaper}
                      variant="outline"
                      className="flex-1"
                    >
                      <Download className="w-4 h-4 mr-2" />
                      Download
                    </Button>
                    <Button
                      onClick={generateWallpaper}
                      variant="outline"
                      className="flex-1"
                      disabled={isGenerating}
                    >
                      <RefreshCw className="w-4 h-4 mr-2" />
                      Regenerate
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Info Card */}
            <Card>
              <CardHeader>
                <CardTitle>Tips for Better Results</CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-gray-600 space-y-2">
                <p>• Be descriptive with colors, lighting, and mood</p>
                <p>• Mention specific art styles for unique looks</p>
                <p>• Use adjectives like "vibrant", "serene", "dramatic"</p>
                <p>• Try combining different elements for creative results</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WallpaperGenerator;